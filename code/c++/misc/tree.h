/// Copyright (c) 2013, Aldrin's Notebook.
#pragma once

#include <memory>
#include <cassert>
#include <ostream>

namespace ajd
{
  struct binary_node_t
  {
    char value;
    binary_node_t(char v): value(v) {}
    std::shared_ptr<binary_node_t> left;
    std::shared_ptr<binary_node_t> right;
  };

  typedef std::shared_ptr<binary_node_t> binary_tree;

  bool is_leaf(binary_tree n) { return !(n->left || n->right); }

  binary_tree make_binary_node(char c) { return std::make_shared<binary_node_t>(c); }

  binary_tree read_binary_tree(const std::string &preorder, const std::string &inorder)
  {
    assert(preorder.size() == inorder.size());

    if (preorder.empty()) { return binary_tree(); }

    std::string::size_type r = inorder.find(preorder[0]);

    std::string left_inorder(inorder, 0, r);
    std::string right_inorder(inorder, r + 1);
    std::string left_preorder(preorder, 1, r);
    std::string right_preorder(preorder, r + 1);

    binary_tree root = make_binary_node(preorder[0]);
    root->left = read_binary_tree(left_preorder, left_inorder);
    root->right = read_binary_tree(right_preorder, right_inorder);

    return root;
  }

  void postorder(binary_tree root, std::ostream &out)
  {
    if (root)
    {
      postorder(root->left, out);
      postorder(root->right, out);
      out << root->value;
    }
  }

  void preorder(binary_tree root, std::ostream &out)
  {
    if (root)
    {
      out << root->value;
      preorder(root->left, out);
      preorder(root->right, out);
    }
  }

  void inorder(binary_tree root, std::ostream &out)
  {
    if (root)
    {
      inorder(root->left, out);
      out << root->value;
      inorder(root->right, out);
    }
  }

}
