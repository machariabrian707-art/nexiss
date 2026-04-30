## Automation and Agent Build Summary

I have completed the build of agents and automations for the Nexiss application, focusing on a flexible and extensible system that can integrate with external tools like n8n via webhooks.

### Key Changes and Implementations:

1.  **Enhanced `pyproject.toml`:** Moved `httpx` from development dependencies to main dependencies, as it's crucial for outbound webhook calls within the automation engine.

2.  **New `src/nexiss/services/automation/executor.py`:**
    *   Introduced a central `execute_action` function to dispatch different types of automation actions.
    *   Implemented `_execute_webhook` to send document processing events to external webhook URLs (e.g., n8n workflows). This includes detailed payload information like `document_id`, `org_id`, `confirmed_type`, `extracted_data`, and `metadata`.
    *   Implemented `_execute_tag_document` to dynamically add tags to a document's `meta_data` field.
    *   Implemented `_execute_run_agent` to trigger internal, specialized Python agents based on their registered names.

3.  **New `src/nexiss/services/automation/agents.py`:**
    *   Created a module to house reusable, internal automation agents.
    *   `PaymentAgent`: Verifies if an organization has an active billing subscription.
    *   `VerificationAgent`: Checks document `type_confidence` and flags documents for manual review if confidence falls below a specified threshold, updating the document's `meta_data` accordingly.
    *   `ExtractionAgent`: Validates `extracted_data` against a list of required fields, failing if any are missing.
    *   `AGENT_REGISTRY`: A dictionary mapping agent names to their respective functions, allowing for dynamic lookup and execution by the `executor`.

4.  **Updated `src/nexiss/services/automation/engine.py`:**
    *   Refactored `execute_internal_automation` to utilize the new `execute_action` from `executor.py`.
    *   The engine now iterates through a rule's `actions` (steps), executing each one and recording its individual result.
    *   The overall `AutomationRun` status now reflects the outcome of all actions, marking the run as `failed` if any single action fails, while still attempting to execute subsequent actions.
    *   Detailed results of each executed action are stored in the `executed_actions` field of the `AutomationRun` model.

5.  **Updated `src/nexiss/services/automation/__init__.py`:** Exposed `execute_action` and `AGENT_REGISTRY` to ensure proper modularity and accessibility within the application.

6.  **Comprehensive `tests/test_automation_engine.py`:**
    *   Added extensive test cases to cover the new `webhook`, `tag_document`, and `run_agent` actions.
    *   Utilized `pytest` fixtures for mocking database sessions (`FakeSession`) and document objects (`mock_document`).
    *   Employed `monkeypatch` to mock `httpx.Client.post` for simulating successful and failed webhook calls.
    *   Included tests for successful and failed scenarios for `payment_agent`, `verification_agent`, and `extraction_agent` with various parameters.
    *   Validated the end-to-end flow with multiple actions, ensuring correct status aggregation and proper updates to `document.meta_data` and `AutomationRun` records.

### How to Leverage these Automations:

*   **n8n Integration:** Define automation rules in Nexiss with a `webhook` action pointing to your n8n workflow. The comprehensive document payload sent to the webhook allows n8n to trigger advanced external processes based on document processing events.
*   **Internal Business Logic:** Use `run_agent` actions to execute Python-based business logic directly within the Nexiss application for tasks requiring direct database interaction or complex calculations, such as credit checks, data validation, or specific document review workflows.
*   **Flexible Tagging:** Automatically tag documents based on content, classification results, or agent decisions, enabling powerful filtering and organization within the system.

This build provides a robust foundation for extending Nexiss's automation capabilities, allowing for both internal, tightly integrated logic and flexible, externally orchestrated workflows.