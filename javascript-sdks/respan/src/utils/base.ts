/**
 * Abstract base classes for Keywords AI API clients
 *
 * This module provides abstract base classes that define common CRUDL (Create, Read, Update, Delete, List)
 * operations for API clients with unified async methods, ensuring consistent interfaces across different resource types.
 */

import { RespanClient } from "./client.js";

/**
 * Abstract base class for unified async API clients with CRUDL operations.
 * 
 * This class provides standard method names for asynchronous operations.
 */
export abstract class BaseAPI<T, TList, TCreate, TUpdate> {
  protected client: RespanClient;

  constructor(options: { apiKey: string; baseUrl?: string }) {
    this.client = new RespanClient(options);
  }

  /**
   * Validate and prepare input data for API requests
   * 
   * @param data - Input data (object)
   * @returns Validated data object
   */
  protected validateInput<TData>(data: TData): TData {
    if (data === null || data === undefined) {
      throw new Error("Input data cannot be null or undefined");
    }
    
    if (typeof data !== 'object') {
      throw new Error("Input data must be an object");
    }
    
    return data;
  }

  /**
   * Prepare data for JSON serialization
   * 
   * @param data - Data to prepare
   * @returns Data ready for JSON serialization
   */
  protected prepareJsonData(data: any): any {
    if (data === null || data === undefined) {
      return data;
    }
    
    // Remove undefined values
    if (typeof data === 'object' && !Array.isArray(data)) {
      const cleaned: any = {};
      for (const [key, value] of Object.entries(data)) {
        if (value !== undefined) {
          cleaned[key] = value;
        }
      }
      return cleaned;
    }
    
    return data;
  }

  // Abstract methods that must be implemented by subclasses
  
  /**
   * Create a new resource
   * 
   * @param createData - Resource creation parameters
   * @returns Created resource information
   */
  abstract create(createData: TCreate): Promise<T>;

  /**
   * List resources with optional filtering and pagination
   * 
   * @param options - List options including pagination and filters
   * @returns List of resources with pagination info
   */
  abstract list(options?: {
    page?: number;
    pageSize?: number;
    [key: string]: any;
  }): Promise<TList>;

  /**
   * Retrieve a specific resource by ID
   * 
   * @param resourceId - ID of the resource to retrieve
   * @returns Resource information
   */
  abstract get(resourceId: string): Promise<T>;

  /**
   * Update a resource
   * 
   * @param resourceId - ID of the resource to update
   * @param updateData - Resource update parameters
   * @returns Updated resource information
   */
  abstract update(resourceId: string, updateData: TUpdate): Promise<T>;

  /**
   * Delete a resource
   * 
   * @param resourceId - ID of the resource to delete
   * @returns Response from the API
   */
  abstract delete(resourceId: string): Promise<{ success: boolean; message?: string }>;
}
