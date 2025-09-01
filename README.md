# Index

- [Problem Statement](#problem-statement)
- [Test Questions](#test-questions)
- [Assumptions](#assumptions)
- [Data Cleaning](#data-cleaning)
- [Data Modelling](#data-modelling)
- [Data QA](#data-qa)

## Problem Statement

- automate data cleaning

- automate modelling through llms

- answer questions based on data

- how much should be deterministic vs how much should be llm

---

- automatically identify and correct inconsistencies in dataset

- handle missing values and potential errors

- rename columns to business friendly names

- simple interface to execute analysis

- easy, medium, hard questions

---

- tracing

- tests

- docs

- deployment

## Test Questions

### Easy:

- Which airline has the most flights listed?
- What are the top three most frequented destinations?
- Number of bookings for American Airlines yesterday.

### Medium:

- Average flight delay per airline.
- Month with the highest number of bookings.

### Hard:

- Patterns in booking cancellations, focusing on specific days or airlines with high cancellation rates.
- Analyze seat occupancy to find the most and least popular flights.

## Assumptions

we should not have to write specific logic for this dataset

- the llm has to decide how to clean the data on its own
- the llm designs the schema on its own
- the llm should be able to answer questions based on the schema

## Data Cleaning

#### Rename columns

- ask llm to get renamer dict for columns

#### Handle missing values

- handle column wise data for all columns based on column type choose the function to fill data

### Improvements/Ideas

- Could have asked to rename column one by ones
- Can use Multivariate Imputation
- Give 100 rows each time till all rows are dones

### Questions

- no missing values present?

- what other inconsistancies?

- what other potential errors?

### Later

- retry = 1 on error
- use langchain or lamaindex

## Data Modelling

### Current Design

- the schema for db should come from llm

- default schema keep it each file seperate

### Ideas

- join the files into one table

- converting the schema to something that is easier to query

- creating whole database schemas instead of one by one

- creating foreign keys between tables

- indexes -> probably not less data

- find and coerce data type for each column

- handle categorical value columns

- handle enums

- need to validate the schema -> retry = 1

## Data QA

### Current Design

- use postgres better sql support

- pass current datetime

- use lama index sql query engine

## Ideas

- potential long context from result of query from db

- history, memory

- think longer

- use multiple queries to get answer

- breaking querys into subqueries

- planning and executing

---
