import { DecoratorConfig } from "@traceloop/node-server-sdk";

// Define the generic function type that matches Traceloop's pattern
export type WithFunctionType = <
    // 'A' represents an array of argument types
    A extends unknown[],
    // 'F' represents a function type that takes those arguments and returns something
    F extends (...args: A) => ReturnType<F>
>(
    config: DecoratorConfig,
    fn: F,
) => Promise<any>;

// Now we can define our specific function types
export type WithAgentType = WithFunctionType;
export type WithTaskType = WithFunctionType;
export type WithWorkflowType = WithFunctionType;
export type DecoratorConfigType = DecoratorConfig;