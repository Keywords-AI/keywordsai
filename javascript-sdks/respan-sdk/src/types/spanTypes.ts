export enum RespanSpanAttributes {
    // Span attributes
    RESPAN_SPAN_CUSTOM_ID = "respan.span_params.custom_identifier",

    // Customer params
    RESPAN_CUSTOMER_PARAMS_ID = "respan.customer_params.customer_identifier",
    RESPAN_CUSTOMER_PARAMS_EMAIL = "respan.customer_params.email",
    RESPAN_CUSTOMER_PARAMS_NAME = "respan.customer_params.name",
    
    // Evaluation params
    RESPAN_EVALUATION_PARAMS_ID = "respan.evaluation_params.evaluation_identifier",

    // Threads
    RESPAN_THREADS_ID = "respan.threads.thread_identifier",

    // Trace
    RESPAN_TRACE_GROUP_ID = "respan.trace.trace_group_identifier",

    // Metadata
    RESPAN_METADATA = "respan.metadata"
}

export const RESPAN_SPAN_ATTRIBUTES_MAP: { [key: string]: string } = {
    customer_identifier: RespanSpanAttributes.RESPAN_CUSTOMER_PARAMS_ID,
    customer_email: RespanSpanAttributes.RESPAN_CUSTOMER_PARAMS_EMAIL,
    customer_name: RespanSpanAttributes.RESPAN_CUSTOMER_PARAMS_NAME,
    evaluation_identifier: RespanSpanAttributes.RESPAN_EVALUATION_PARAMS_ID,
    thread_identifier: RespanSpanAttributes.RESPAN_THREADS_ID,
    custom_identifier: RespanSpanAttributes.RESPAN_SPAN_CUSTOM_ID,
    trace_group_identifier: RespanSpanAttributes.RESPAN_TRACE_GROUP_ID,
    metadata: RespanSpanAttributes.RESPAN_METADATA
};

// Type for valid span attribute values
export type SpanAttributeValue = string | number | boolean | Array<string | number | boolean>;
