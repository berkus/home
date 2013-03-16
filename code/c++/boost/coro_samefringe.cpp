#include <misc/tree.h>
#include <boost/bind.hpp>
#include <boost/coroutine/all.hpp>

typedef ajd::binary_tree<char> tree;

typedef boost::coroutines::coroutine<char()> generator;

bool is_leaf(tree::node l) { return !(l->left || l->right); }

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

int main()
{
  tree::node red = tree::read_tree("(-(-(-(X)(R))(-(I)(N)))(-(G)(E)))");
  tree::node blue1 = tree::read_tree("(-(-(-(F)(R))(-(I)(N)))(-(G)(E)))");
  tree::node blue2 = tree::read_tree("(-(-(-(-(-(F)(R))(I))(N))(G))(E))");
  tree::node blue3 = tree::read_tree("(-(-(-(-()(F))(R))(I))(-(-(-(N)())(G))(E))");
  assert(same_fringe(blue1, blue2));
  assert(same_fringe(blue2, blue3));
  assert(!same_fringe(red, blue1));
}
