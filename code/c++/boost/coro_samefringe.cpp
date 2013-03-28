/// Copyright (c) 2013, Aldrin's Notebook.
/// http://opensource.org/licenses/BSD-2-Clause

#include <misc/tree.h>
#include <boost/bind.hpp>
#include <boost/coroutine/all.hpp>

typedef ajd::binary_tree<char> tree;

typedef boost::coroutines::coroutine<char()> generator;

bool is_leaf(tree::node l) { return !(l->left || l->right); }

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

int main()
{
  tree::node empty = tree::read_tree("");
  tree::node red = tree::read_tree("(-(-(-(X)(R))(-(I)(N)))(-(G)(E)))");
  tree::node blue1 = tree::read_tree("(-(-(-(F)(R))(-(I)(N)))(-(G)(E)))");
  tree::node blue2 = tree::read_tree("(-(-(-(-(-(F)(R))(I))(N))(G))(E))");
  tree::node blue3 = tree::read_tree("(-(-(-(-()(F))(R))(I))(-(-(-(N)())(G))(E))");
  tree::node diff = tree::read_tree("(-(-(-(-()(F))(R))(I))(-(-(-(N)())(G))())");
  assert(!same_fringe(empty, red));
  assert(!same_fringe(red, blue1));
  assert(same_fringe(empty, empty));
  assert(same_fringe(blue1, blue2));
  assert(same_fringe(blue2, blue3));
  assert(!same_fringe(blue2, diff));
}
