// Copyright (c) 2013. Aldrin's Notebook [http://aldrin.co]

package co.aldrin.spring.quartz;

import org.quartz.*;
import org.springframework.context.ApplicationContext;

import java.util.Map;

/**
 * aldrin 15/03/13
 */
public class NonsenseJob implements Job {
    @Override
    public void execute(JobExecutionContext context) throws JobExecutionException {
        try {
            /* Here's how we get our hands on a bean. */
            SchedulerContext schedulerContext = context.getScheduler().getContext();
            ApplicationContext applicationContext = (ApplicationContext) schedulerContext.get("applicationContext");
            Map testData = applicationContext.getBean("testData", Map.class);
            System.out.println("testData = " + testData);
        } catch (SchedulerException e) {
            e.printStackTrace();
        }
    }
}
