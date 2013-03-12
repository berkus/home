Date: 08/03/2013
Tags: C++, Boost
slug: coroutines
Title: Coroutines in C++

Structured programming decomposes a complex task into smaller units called _subroutines_ that are
then stitched together in an intricate fabric of callers and callees to get the task done. While
that seems like the natural thing to do, the operational semantics associated with the invocation of
these routines; things like calling conventions, variable scopes, their lifetimes, etc. are more or
less _conventions_. An interesting deviation from these conventions is a coroutine.

A subroutine has a single entry point. All data local to a subroutine is initialized upon entry and
is cleaned up when the subroutine returns to its caller. The next call, if any, starts all over
again and there are no local residues carried over from the last time (ignoring global side effects,
of course.) In contrast, a coroutine can have multiple entry points and its execution for a given
invocation depends on where the last one left and how it altered the local state. These
multiple-entry semantics make coroutines an nice abstraction for certain class of problems.

[Boost.Coroutine][coro].

#### Generators

Let's start with a slightly academic problem that is probably the simplest one that is _better_
solved with a coroutine than with a subroutine. The problem is to write a routine to test whether
two binary trees have the _same fringe_, i.e. if they have e exactly the same leaves reading from
left to right. For example, the blue leaf trees in the figure below have the same fringe as each
other while none of them have the same fringe as the red leaf tree.

<img src="/static/images/samefringe.png">

How would we write a routine that implements this check given two [binary trees][mytree]?

The first solution that comes to mind is to compare the left-first post-order traversals of the two
trees and return true if they're the same. That'd work; however, it would travese both trees
completely before returning its answer. There's no way for us to return a `true` result before
looking at _all_ the leaves in the both trees but it only takes one mismatch before we can safely
return `false`. So given the red and any of the blue trees, our routine wouldn't be optimal if it
didn't return `false` after looking at just the left most leafs of the two trees.

To be optimal, we need to return early (after every leaf) and the resume our traversals from where
we last left. This is exactly the kind of thing that coroutine are best at and also exactly the kind
of thing a _true_ subroutine cannot do. Of course, you can defy subroutine semantics, maintain state
between executions, have an elaborate conditional control flow mechanism that drops you right where
you need to be, but in doing all this, all you'd be doing is implementing the infrastructure for
coroutines in your language. A better choice would be to use a generic coroutine implementation in
your programming language, which happens to be Boost.Coroutines for us right now.

Here's the solution then

``` c++
#include <misc/tree.h>
#include <boost/bind.hpp>
#include <boost/coroutine/all.hpp>

typedef ajd::binary_tree<char> tree;

typedef boost::coroutines::coroutine<char()> leaf_iterator;

bool is_leaf(tree::node l) { return !(l->left || l->right); }

void leaves(leaf_iterator::caller_type &yield, tree::node &node)
{
  if (node)
  {
    leaves(yield, node->left);
    leaves(yield, node->right);
    if (is_leaf(node)) { yield(node->value); }
  }
}

bool same_fringe(tree::node one, tree::node two)
{
  leaf_iterator leaves1(boost::bind(leaves, _1, one));
  leaf_iterator leaves2(boost::bind(leaves, _1, two));
  while (leaves1 && leaves2)
  {
    if (leaves1.get() != leaves2.get()) { return false; }
    leaves1();
    leaves2();
  }
  return true;
}

void test_same_fringe()
{
  tree::node red = tree::read_tree("(-(-(-(X)(R))(-(I)(N)))(-(G)(E)))");
  tree::node blue1 = tree::read_tree("(-(-(-(F)(R))(-(I)(N)))(-(G)(E)))");
  tree::node blue2 = tree::read_tree("(-(-(-(-(-(F)(R))(I))(N))(G))(E))");
  tree::node blue3 = tree::read_tree("(-(-(-(-()(F))(R))(I))(-(-(-(N)())(G))(E))");
  assert(same_fringe(blue1, blue2));
  assert(same_fringe(blue2, blue3));
  assert(!same_fringe(red, blue1));
}
```

A coroutine definition starts with chosing what values it is expected to generate and what input it
needs to do its work. In the current example, our coroutine must generate the leaf node values
without taking any input so its function signature would be `char()`. This signature is plugged into
the `boost::coroutines::coroutine` template to generate the type of coroutine we need
`leaf_iterator`. Note that the function signature is not the signature of the actual coroutine, it
is just the signature for theNext we define the actual coroutine implementation which has a prescribed signature





[dabeaz]: http://dabeaz.com/coroutines/
[mytree]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/misc/tree.h
[coro]: http://www.boost.org/doc/libs/release/libs/coroutine/doc/html/index.html
