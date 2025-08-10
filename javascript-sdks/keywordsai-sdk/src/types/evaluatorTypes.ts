import { PaginatedResponseType } from "./genericTypes.js";

export interface Evaluator {
    id: string;
    name: string;
    slug: string;
    description?: string;
    created_at: string;
    updated_at: string;
}

export type EvaluatorList = PaginatedResponseType<Evaluator>;
