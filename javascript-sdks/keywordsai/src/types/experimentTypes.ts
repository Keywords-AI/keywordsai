// Re-export experiment types from keywordsai-sdk
export type {
  ExperimentType as Experiment,
  ListExperimentsResponse as ExperimentList,
  CreateExperimentRequest as ExperimentCreate,
  ExperimentColumnType,
  ExperimentRowType,
  ExperimentResultItemType,
  AddExperimentRowsRequest,
  RemoveExperimentRowsRequest,
  UpdateExperimentRowsRequest,
  AddExperimentColumnsRequest,
  RemoveExperimentColumnsRequest,
  UpdateExperimentColumnsRequest,
  RunExperimentRequest,
  RunExperimentEvalsRequest,
} from "@keywordsai/keywordsai-sdk";

// Create a simple update type for experiment metadata
export interface ExperimentUpdate {
  /** Update request for experiment metadata */
  name?: string;
  description?: string;
}
