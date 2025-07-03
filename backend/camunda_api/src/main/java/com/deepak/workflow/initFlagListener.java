package com.deepak.workflow;

import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.ExecutionListener;
import java.util.logging.Logger;

public class initFlagListener implements ExecutionListener {

    private final logger logger = logger.logger.getLogger(initFlagListener.class.getName());

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        execution.setVariable("flag", false);
        logger.info("Flag variable initialized to false on start event.");
    }
}