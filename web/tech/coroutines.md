Date: 08/03/2013
Tags: C++, Boost
slug: coroutines
Title: Coroutines in C++

<!-- Structured programming breaks a complex task into smaller units called _subroutines_ that are then -->
<!-- stitched together in an intricate fabric of callers and callees to get the task done. While that -->
<!-- seems like the natural thing to do, the operational semantics associated with the invocation of -->
<!-- these routines; things like calling conventions, variable scopes, their lifetimes, etc. are more or -->
<!-- less _conventions_. An interesting deviation from these conventions is a coroutine. -->

A subroutine has a single entry point. All data local to it is initialized upon entry and is cleaned
up when it returns. The next call, if any, starts all over again and there are no local residues
carried over from the last time (ignoring global side effects, which we're advised to avoid anyway.)
Subroutines are the most popular form of structuring a program into small manageable chunks but
they aren't the only one. An interesting alternative is a coroutine.

The ideal subroutine is a mathematical function; you give it inputs and it returns the results of
the computation back. A coroutine isn't atomic like that, it can _yield_ control back to the caller
as soon as there are partial results that can be of use. It can also _resume_ the computation from
where it left when the caller invokes it again after using the partial results. These yield-resume
semantics make coroutines better abstractions than subroutines for certain problems.

In the following, we walk through some such problems and implement them using
[Boost.Coroutine][coro].

#### Generators

Let's start with simple generators. Consider the problem of writing a routine that checks if two
binary trees have the _same fringe_ i.e.  if they have exactly the same leaves reading from left to
right. The blue trees below all have the same fringe other while none of them have the same fringe
as the red one.

<img src="/static/images/samefringe.png">

How would we write a routine that takes two [binary trees][mytree] and checks if they have the same fringe?

Simple, check if the post-order traversals of the two trees is the same. That works but is
suboptimal as it requires us to access _all_ leaf nodes in both the trees, always. Looking at all
nodes is _necessary_ before returning a `true` but we should be able to return `false` sooner. For
example, given the red and any of the blue trees from above, we can return a `false` after looking
at just the first node from the two trees. To do that we would have to compare the two trees one
leaf at a time. The routine would have to descend down to the first leaf and yield control back to
the caller with the leaf value. The caller would then compare the values of two leaves received and
return `false` if they don't match or return control back to the routines to resume their
traversals.  Pause a little while here and consider writing a subroutine that can do this.

You _can_ twist a subroutine's arms to make it do similar tricks but this 'yield partial results and
resume' situation is best handled by coroutines. This [python enhancement proposal][pep] has more
motivating examples if I've failed to convince you.

[Here's][sfcoro] a coroutines based implementation for the problem above:

```c++
#include <misc/tree.h>
#include <boost/bind.hpp>
#include <boost/coroutine/all.hpp>

typedef ajd::binary_tree<char> tree;

typedef boost::coroutines::coroutine<char()> generator;

void next_leaf(generator::caller_type &yield, tree::node &node)
{
  if (node)
  {
    next_leaf(yield, node->left);
    next_leaf(yield, node->right);
    if (is_leaf(node)) { yield(node->value); }
  }
}

bool same_fringe(tree::node one, tree::node two)
{
  generator leaf1(boost::bind(next_leaf, _1, one));
  generator leaf2(boost::bind(next_leaf, _1, two));

  for (; (leaf1 && leaf2); leaf1(), leaf2())
  {
    if (leaf1.get() != leaf2.get())
    {
      return false;
    }
  }

  return true;
}
```

Let's use this example as a primer on Boost.Coroutine usage. If you were (as I was) hoping that
syntax to be as neat as it is for Python generators, it isn't. The key thing to note is that the
_logical coroutine_ we're trying to write is different from the _acutal function_ (`next_leaf`) that
Boost.Coroutine needs. The two are related, but they're not the same (as in Python.)

We start with asking ourselves: **what is the logical signature of the coroutine?** That is, if it
was a normal C++ function what would it signature be. The answer depends on the type of the partial
result generated and the inputs (per invocation) taken to produce it. For our example, that'd be
`char()` because the caller expects the coroutine to produce the `char` value stored in the next
leaf nodes in the traversal. This logical signature is plugged into the
`boost::coroutines::coroutine` template to get the coroutine type `generator`. 

The choice of inputs to the coroutine is slightly tricky. wasn't obvious to me first. It is possible
for the coroutine to expect an input for every invocation, but the case in our example is
different. We need



[pep]:http://www.python.org/dev/peps/pep-0255/
[dabeaz]: http://dabeaz.com/coroutines/
[mytree]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/misc/tree.h
[sfcoro]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/misc/tree.h
[coro]: http://www.boost.org/doc/libs/release/libs/coroutine/doc/html/index.html
