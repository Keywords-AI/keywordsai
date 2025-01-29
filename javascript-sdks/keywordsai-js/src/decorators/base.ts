import { 
    withAgent as withTraceloopAgent, 
    withTask as withTraceloopTask, 
    withWorkflow as withTraceloopWorkflow,
} from "@traceloop/node-server-sdk";
import { WithAgentType, WithTaskType, WithWorkflowType } from "../types/decoratorTypes";

export const withAgent: WithAgentType = withTraceloopAgent;
export const withTask: WithTaskType = withTraceloopTask;
export const withWorkflow: WithWorkflowType = withTraceloopWorkflow;