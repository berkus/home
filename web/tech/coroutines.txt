Date: 08/03/2013
Tags: C++, Boost
slug: coroutines
Title: Coroutines in C++ (incomplete...)

The ideal subroutine is a mathematical function; you give it inputs and it returns the results of
the computation. It has a single entry point, all data local to it is initialized upon entry and is
cleaned up when it returns back to the caller. The next call, if any, starts all over again and no
local residues are carried over from the last time. A coroutine is an interesting deviation from
these well set conventions. Unlike a subroutine, a coroutine is not required to be atomic; it can
_yield_ control back to the caller as soon as there are partial results that can be used. Moreover,
it can _resume_ the computation from where it left when the invoked again.

These yield-resume semantics make coroutines a better abstraction for certain problems. In the
following, I walk through some such problems and implement their solutions using
[Boost.Coroutine][coro]. Let's start with [generators][pep].

#### Generators

Consider the problem of writing a routine that checks if two binary trees have the _same fringe_
i.e.  if they have exactly the same leaves reading from left to right. For example, the blue trees
below all have the same fringe while none of them have the same fringe as the red one.

<img src="/static/images/samefringe.png">

How would we write a routine that takes two [binary trees][mytree] and checks if they have the same
fringe?

Simple, check if the post-order traversals of the two trees are the same. That works but is
suboptimal as it requires us to access _all_ leaf nodes in both the trees, always. Looking at all
nodes is _necessary_ before returning a `true` but we should be able to return `false` sooner. For
example, given the red and any of the blue trees from above, we can return a `false` after looking
at just the first node from the two trees. To do that we would have to compare the trees one leaf at
a time. The routine would have to descend down to the first leaf and yield control back to the
caller with the leaf value. The caller would then compare the values of two leaves received and
return `false` if they don't match or return control back to the routines to resume their
traversals.  Pause a little while here and consider writing a subroutine that can do this.

The example, though academic, gives us insight that a coroutine based generator is better when it
makes sense to return partial results early and resume the remaining computation only if
needed. [Here's][sfcoro] how we do that for the problem above:

``` c++
#include <misc/tree.h>
#include <boost/bind.hpp>
#include <boost/coroutine/all.hpp>

typedef ajd::binary_tree<char> tree;
typedef boost::coroutines::coroutine<char()> generator;

void next_leaf(generator::caller_type &caller, tree::node &node)
{
  if (node)
  {
    next_leaf(caller, node->left);
    next_leaf(caller, node->right);
    if (is_leaf(node)) { caller(node->value); }
  }
}

bool same_fringe(tree::node one, tree::node two)
{
  generator leaf1(boost::bind(next_leaf, _1, one));
  generator leaf2(boost::bind(next_leaf, _1, two));

  while (leaf1 || leaf2) // while one of the trees has a next leaf
  {
    if (leaf1 && leaf2)  // if both have a next leaf
    {
      if (leaf1.get() != leaf2.get()) // compare the next leaf
      {
        return false; // next leaves don't match. return false.
      }
      leaf1(); // advance the first tree traversal
      leaf2(); // advance the second tree traversal
    }
    else // one tree has more leaves than the other.
    {
      return false; // leaf count mismatch. return false.
    }
  }
  return true; // no mismatches found, return true.
}
```

If you were (as I was) hoping that syntax would be as neat as it is for Python generators, it
isn't. The first thing to get used to is that the _logical coroutine_ we want to write is different
from the _actual function_ we have to write (i.e. `next_leaf`.) The second is to realize that
coroutines work in pairs; they don't _return_ back to their caller, instead, they _call_ the caller
back.

With these two things in mind, consider the routine `same_fringe`. The first thing we do is create
two instances of type `generator` each bound to one of the roots of the trees we're comparing.  The
`generator` type is an instantiation of the `boost::coroutines::coroutine` template class with the
_logical_ signature of the coroutine plugged in. Here, this logical signature is `char()` because
the routine is expected to return `char` values stored in the tree leaves.

Next, remember that the coroutine will not _return_ these leaf values like a subroutines would,
instead, it will call another coroutine that represents the caller. A reference to this peer
coroutine is passed as the first argument to `next_leaf`. The actual type of this first argument is
`boost::coroutines::coroutine<void(char)` and the same is also available as the convenience typedef
`generator::caller_type`. Think about it and it'll make sense.

The rest of the comparison logic is implemented using three member functions of the
`boost::coroutines::coroutines` class. The first is the conversion to `bool` that allows us to check
if the coroutine is active (it stays active till `next_leaf` ends). The second is a function call
operator that resumes a coroutine execution. So `leaf1()` in `same_fringe` resumes `next_leaf` and
executes its code till it yields back by calling its caller. Note that `caller(node->value)` inside
`next_leaf` does exactly the same thing, i.e. resumes the execution of `same_fringe`. The last
method used is `get` that is an accessor for the result computed by the last invocation of the
coroutine. The return type here is `char` and we use it to compare the leaf nodes.

Hopefully, that made sense.

#### Incomplete
This post is incomplete. Have more samples

[dabeaz]: http://dabeaz.com/coroutines/
[pep]:http://www.python.org/dev/peps/pep-0255/
[mytree]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/misc/tree.h
[sfcoro]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/boost/coro_samefringe.cpp
[coro]: http://www.boost.org/doc/libs/release/libs/coroutine/doc/html/index.html
