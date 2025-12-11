# GSP Pydantic API Reference

The GSP Pydantic module provides serialization and deserialization capabilities using Pydantic models, enabling data validation and JSON schema generation for GSP objects.

## Overview

::: gsp_pydantic
    handler: python
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Serializer Module

The serializer module contains the serialization and parsing utilities for converting GSP objects to and from Pydantic models.

::: gsp_pydantic.serializer
    handler: python
    options:
      show_root_heading: true
      show_source: true
      members_order: source

### Pydantic Serializer

::: gsp_pydantic.serializer.pydantic_serializer
    handler: python
    options:
      show_root_heading: true
      show_source: true

### Pydantic Parser

::: gsp_pydantic.serializer.pydantic_parser
    handler: python
    options:
      show_root_heading: true
      show_source: true

## Types Module

The types module defines Pydantic models for GSP data structures, providing validation and schema generation.

::: gsp_pydantic.types
    handler: python
    options:
      show_root_heading: true
      show_source: true
      members_order: source

### Pydantic Dict

::: gsp_pydantic.types.pydantic_dict
    handler: python
    options:
      show_root_heading: true
      show_source: true

### Pydantic Types

::: gsp_pydantic.types.pydantic_types
    handler: python
    options:
      show_root_heading: true
      show_source: true
