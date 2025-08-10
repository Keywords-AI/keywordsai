export interface RangeType {
    min: number;
    max: number;
}

export interface ParamType {
    name: string;
    type?: "string" | "number" | "boolean" | "object" | "array" | "int";
    default?: string | number | boolean | object | any[] | null;
    range?: RangeType;
    description?: string;
    required?: boolean;
}

export interface PaginatedResponseType<T> {
    results: T[];
    count: number;
    next?: string;
    previous?: string;
}
