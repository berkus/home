#include<vector>
#include<gtest/gtest.h>
#include<boost/weak_ptr.hpp>
#include<boost/shared_ptr.hpp>
#include<boost/enable_shared_from_this.hpp>

using std::vector;
using boost::weak_ptr;
using boost::shared_ptr;
using boost::enable_shared_from_this;

TEST(StudentCourse, BadUsageDoubleDelete)
{
  class Student;
  class Course
  {
  public:
    void enroll(shared_ptr<Student> s)
    {
      register_.push_back(s);
    }
  private:
    vector<shared_ptr<Student>> register_;
  };
  class Student
  {
  public:
    void offer(Course &c)
    {
      if (interested_in(c))
      { c.enroll(shared_ptr<Student>(this)); }
    }

  private:
    bool interested_in(Course &c)
    {
      return true;
    }
  };
  ASSERT_DEATH(
  {
    Course math;
    shared_ptr<Student> s(new Student);
    s->offer(math);
  }, ".*");
}

TEST(StudentCourse, BadUsageLeaks)
{
  class Student;
  class Course
  {
  public:
    void enroll(shared_ptr<Student> s)
    {
      register_.push_back(s);
    }
  private:
    vector<shared_ptr<Student>> register_;
  };
  class Student
  {
  public:
    void offer(Course &c)
    {
      if (interested_in(c))
      { c.enroll(self_); }
    }

    void set_this(shared_ptr<Student> self)
    {
      self_ = self;
    }

  private:
    shared_ptr<Student> self_;
    bool interested_in(Course &c)
    {
      return true;
    }
  };
  Course math;
  shared_ptr<Student> s(new Student);
  s->set_this(s);
  s->offer(math);
  ASSERT_EQ(3, s.use_count());
}

TEST(StudentCourse, Works)
{
  class Student;
  class Course
  {
  public:
    void enroll(shared_ptr<Student> s)
    {
      register_.push_back(s);
    }
  private:
    vector<shared_ptr<Student>> register_;
  };
  class Student
  {
  public:
    void offer(Course &c)
    {
      if (interested_in(c))
      { c.enroll(self_.lock()); }
    }

    void set_this(shared_ptr<Student> self)
    {
      self_ = self;
    }

  private:
    weak_ptr<Student> self_;
    bool interested_in(Course &c)
    {
      return true;
    }
  };
  Course math;
  shared_ptr<Student> s(new Student);
  s->set_this(s);
  s->offer(math);
  ASSERT_EQ(2, s.use_count());
}

TEST(StudentCourse, Best)
{
  class Student;
  class Course
  {
  public:
    void enroll(shared_ptr<Student> s)
    {
      register_.push_back(s);
    }
  private:
    vector<shared_ptr<Student>> register_;
  };
  class Student : public enable_shared_from_this<Student>
  {
  public:
    void offer(Course &c)
    {
      if (interested_in(c))
      { c.enroll(shared_from_this()); }
    }
  private:
    bool interested_in(Course &c)
    {
      return true;
    }
  };
  Course math;
  shared_ptr<Student> s(new Student);
  s->offer(math);
  ASSERT_EQ(2, s.use_count());
}
