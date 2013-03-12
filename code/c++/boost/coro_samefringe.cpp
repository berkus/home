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
