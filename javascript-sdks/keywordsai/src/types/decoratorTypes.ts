// Decorator types for KeywordsAI SDK
// This file contains type definitions for decorators used in the SDK

export interface DecoratorOptions {
  // Add decorator options here as needed
}

// Add more decorator types as needed
export type DecoratorFunction = (target: any, propertyKey?: string, descriptor?: PropertyDescriptor) => any; 