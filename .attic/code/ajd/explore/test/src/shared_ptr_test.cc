#include<gtest/gtest.h>
#include<boost/weak_ptr.hpp>
#include<boost/shared_ptr.hpp>

using boost::weak_ptr;
using boost::shared_ptr;

TEST(SmartPtrs, BasicUsage)
{
    shared_ptr<int> p(new int);
    {
        shared_ptr<int> q(p);
        ASSERT_FALSE(p.unique() || q.unique());
        ASSERT_EQ(2, q.use_count());
    }
    ASSERT_TRUE(p.unique());
}

TEST(SmartPtrsDeathTest, BadUsageDoubleDelete)
{
    ASSERT_DEATH(
    {
        int *i = new int;
        shared_ptr<int> p(i);
        {
            shared_ptr<int> r(i);
        }
    }, ".*");
}

TEST(SmartPtrs, WeakPtrUsage)
{
    shared_ptr<int> p(new int);
    weak_ptr<int> w(p);
    {
        ASSERT_EQ(1, p.use_count());
        shared_ptr<int> q = w.lock();
        ASSERT_EQ(2, q.use_count());
    }
    ASSERT_EQ(1, w.use_count());
    p.reset();
    ASSERT_TRUE(w.expired());
}
