Date: 19/05/2010
Tags: Security
Slug: do-privileged
Title: Using doPrivileged

The `doPrivileged` API enables a few use cases which wouldn't be possible without it.  It is quite
neatly [documented][doc] but it took me a while to really get a hang of its usage. This note shares
my understanding on the usage and the capabilities of this neat little extension to the Java access
control framework.

Consider the task of implementing the following protected resource:

``` java
// code-base 'file:///code/resource'
public class Resource {
  public void read() {
    RuntimePermission permission = new RuntimePermission("resource.read");
    AccessController.checkPermission(permission);
    System.out.println("read"); // actual read implementation 
  }

  public void write() {
    RuntimePermission permission = new RuntimePermission("resource.write");
    AccessController.checkPermission(permission);
    System.out.println("write"); // actual write implementation
  }
}
```

The resource has two operations which check for the necessary permission before executing the the
actual implementation. This allows us to control access to the operations even in cases when the
resource is used from arbitrary user code. For example, we can implement read-only access to the
resource by enforcing the following policy (assuming that the resource and user classes belong to
separate code-bases)

```
grant codebase "file:///code/resource" {
 permission java.lang.RuntimePermission "resource.####";
};
grant codebase "file:///code/user" {
 permission java.lang.RuntimePermission "resource.read";
};
```

Such a strict policy might limit a few useful use cases. For example, it might be useful to allow
the user code to write to the resource, if we can program reliable tests that it writes responsibly
without corrupting the resource. One possible way to implement such a system is to introduce a
wrapper between the user and the resource which intercepts all the writes and block the
illegal/harmful ones. Something like the following:

``` java
// code-base 'file:///code/resource'
public class ResourceWrapper {
  private Resource resource;

  public ResourceWrapper(Resource r){ resource = r; }

  public void write() {
    if(writeIsBad) // filter out the bad stuff.
     return; 

    resource.write();
  }
}
```

As we own and control the wrapper code we grant it all permissions over the resource, hoping that
well behaved user code will be able to write to the resource by invoking the wrapper instead of the
resource directly.

The trouble is that the access controller, by default, requires that the needed permission is
granted to _every_ protection domain on the call stack. _We_ know that wrapper is trusted and
guarantees that the writes it lets through are harmless regardless of where they orignated from, but
the access controller doesn't. What we need is a mechanism by which a trusted protection domain can
confer its own permissions to a call originating from an untrusted domain. And that, is exactly,
what the `doPrivileged` does.

All that a `doPrivileged` call does is mark the protection domain which invoked it as
_privileged_. If a _privileged_ domain on the stack has the required permission, the call succeeds
regardless of whether or not the domains below it on the call-stack have the permission. So if our
wrapper is modified as follows:

``` java
// code-base 'file:///code/resource'
public class ResourceWrapper {
  //...
  public void write() {
    if(writeIsBad) // filter out the bad stuff.
      return; 

    AccessController.doPrivileged(new PrivilegedAction() {
        public Object run() {
          resource.write();
          return null;
        }
      });
  }
}
```

The users of the resource can invoke regulated writes as follows:

``` java
// code-base 'file:///code/user'
public class User {
  public static void main(String args[]) {
    Resource resource = new Resource();
    ResourceWrapper watchfulEyes = new ResourceWrapper(resource);
    // can operate directly
    resource.read(); // we have the permission ourself.
    // operate in a sandbox
    watchfulEyes.write(); // we don't have the permission ourselves.
  }
}
```

#### limiting the permissions

Note that when we used the privileged block to enable the wrapper permissions to an untrusted
invoker, we enabled /all/ of them for the scope of that call. This might be a problem, for example,
consider the case where our resource was implemented as follows:

``` java
public class Resource {
  //...
  public void write() {
    RuntimePermission permission = new RuntimePermission("resource.write");
    AccessController.checkPermission(permission);

    if(!existsAlready) // the resource does not exist
      create(); // create it first.

    System.out.println("write"); // do the actual write.
  }
 
  public void create() {
    RuntimePermission permission = new RuntimePermission("resource.create");
    AccessController.checkPermission(permission);
    System.out.println("create"); // do the actual 'create'.
  }
}
```

In this version, if a write is invoked on a resource which does not exist already, the
implementation will create it first.  If our intention was only to allow the user code to write to
existing resources but not to give them the ability to create new ones, our existing wrapper won't
be able to enforce it. In invoking the privileged call it does not specify how many of its own
permissions are be to enabled for the user-code, and thus ends up giving the `create` permission
too.

To fix this behavior we need a mechanism to specify a subset of permissions which the trusted
protection domain wishes to confer for a privileged call and that is achieved by specifying an
`AccessControlContext` parameter in the privileged call.  Consider the following updated wrapper
implementation:

``` java
// code-base 'file:///code/resource'
public class ResourceWrapper {
  //...
  public void write() {
    // specify a subset of permission which need to be enabled
    Permissions subset = new Permissions();
    subset.add(new RuntimePermission("resource.write"));
    AccessControlContext context = new AccessControlContext
      ({ new ProtectionDomain(null,subset) });
    AccessController.doPrivileged(new PrivilegedAction() {
        public Object run() {
          resource.write();
          return null;
        }
      }, context);
  }
```

Now, the wrapper explicitly specifies that it only wants to enable the write permission for its
caller. This way, user code which writes to existing resources will work as before but attempts to
use the wrapper code as short-cut to create new resources would fail.

That's it.

[doc]:http://java.sun.com/j2se/1.4.2/docs/guide/security/doprivileged.html
