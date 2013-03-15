// Copyright (c) 2013. Aldrin's Notebook [http://aldrin.co]

package co.aldrin.spring.quartz;

import org.junit.Test;
import org.quartz.Scheduler;
import org.quartz.SchedulerException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.AbstractJUnit4SpringContextTests;

import static junit.framework.TestCase.assertTrue;

/**
 * aldrin 15/03/13
 */

@ContextConfiguration("classpath:scheduler-test.xml")
public class SchedulerTest extends AbstractJUnit4SpringContextTests {
    @Autowired
    Scheduler scheduler;

    @Test
    public void schedulerStarts() throws SchedulerException {
        assertTrue(scheduler.isStarted());
    }
}
