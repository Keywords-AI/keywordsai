export enum KeywordsAISpanAttributes {
    // Span attributes
    KEYWORDSAI_SPAN_CUSTOM_ID = "keywordsai.span_params.custom_identifier",

    // Customer params
    KEYWORDSAI_CUSTOMER_PARAMS_ID = "keywordsai.customer_params.customer_identifier",
    KEYWORDSAI_CUSTOMER_PARAMS_EMAIL = "keywordsai.customer_params.email",
    KEYWORDSAI_CUSTOMER_PARAMS_NAME = "keywordsai.customer_params.name",
    
    // Evaluation params
    KEYWORDSAI_EVALUATION_PARAMS_ID = "keywordsai.evaluation_params.evaluation_identifier",

    // Threads
    KEYWORDSAI_THREADS_ID = "keywordsai.threads.thread_identifier",

    // Trace
    KEYWORDSAI_TRACE_GROUP_ID = "keywordsai.trace.trace_group_identifier",

    // Metadata
    KEYWORDSAI_METADATA = "keywordsai.metadata"
}

export const KEYWORDSAI_SPAN_ATTRIBUTES_MAP: { [key: string]: string } = {
    customer_identifier: KeywordsAISpanAttributes.KEYWORDSAI_CUSTOMER_PARAMS_ID,
    customer_email: KeywordsAISpanAttributes.KEYWORDSAI_CUSTOMER_PARAMS_EMAIL,
    customer_name: KeywordsAISpanAttributes.KEYWORDSAI_CUSTOMER_PARAMS_NAME,
    evaluation_identifier: KeywordsAISpanAttributes.KEYWORDSAI_EVALUATION_PARAMS_ID,
    thread_identifier: KeywordsAISpanAttributes.KEYWORDSAI_THREADS_ID,
    custom_identifier: KeywordsAISpanAttributes.KEYWORDSAI_SPAN_CUSTOM_ID,
    trace_group_identifier: KeywordsAISpanAttributes.KEYWORDSAI_TRACE_GROUP_ID,
    metadata: KeywordsAISpanAttributes.KEYWORDSAI_METADATA
};

// Type for valid span attribute values
export type SpanAttributeValue = string | number | boolean | Array<string | number | boolean>;
