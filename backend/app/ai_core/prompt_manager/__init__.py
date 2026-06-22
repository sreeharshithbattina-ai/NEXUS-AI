import json
from typing import Dict, Any, Optional, List
from ..interfaces.prompt import PromptTemplate

class VersionedPrompt(PromptTemplate):
    """Concrete implementation of a versioned, interpolatable prompt template."""
    def __init__(self, template: str, version: str):
        self._template = template
        self._version = version

    def render(self, variables: Dict[str, Any]) -> str:
        res = self._template
        for k, v in variables.items():
            placeholder = f"{{{{{k}}}}}"
            res = res.replace(placeholder, str(v))
        return res

    @property
    def version(self) -> str:
        return self._version

class PromptManager:
    """
    Central repository formatting system prompts, dynamic context payloads,
    and injection constraints with explicit release version records.
    """
    def __init__(self):
        # Master repository of versioned templates
        self._templates: Dict[str, VersionedPrompt] = {
            "system_ceo": VersionedPrompt(
                "You are NEXUS CEO Agent. Your role is high-level strategic reasoning and coordination.\n"
                "System Core Guidelines: Always synthesize precise tasks.\n"
                "Current Workspace Context: \n"
                "{{context}}\n"
                "Relevant Memories: {{memories}}\n"
                "Retrieved Documents (RAG): {{documents}}\n"
                "User Intent: {{user_intent}}",
                "1.0.3"
            ),
            "system_planner": VersionedPrompt(
                "You are NEXUS Planner Agent. You partition complex tasks into micro-stages.\n"
                "Rules:\n"
                "1. Divide user request into sequential stages.\n"
                "2. Determine estimated tools required for each step.\n"
                "3. Define estimated executing agent specialty for each step.\n"
                "Context Matrix: {{context}}\n"
                "User Task: {{user_intent}}",
                "1.2.0"
            ),
            "system_reasoner": VersionedPrompt(
                "You are NEXUS Reasoner Agent. Audit the proposed plan for logical inconsistencies, "
                "missing variables, security hazards, and estimate execution risk.\n"
                "Input Plan: {{input_plan}}\n"
                "User Context: {{context}}\n"
                "Analyze and confirm completeness or specify missing details.",
                "1.1.1"
            ),
            "system_executor": VersionedPrompt(
                "You are NEXUS Executor Agent. Formulate actions calling the target systems.\n"
                "Plan Steps: {{approved_plan}}\n"
                "Active Context: {{context}}\n"
                "Retrieved Chunk: {{rag_chunks}}\n"
                "System State: {{system_state}}\n"
                "Perform operations step by step.",
                "2.0.0"
            ),
            "system_agent_default": VersionedPrompt(
                "NEXUS Core Shell instruction: Proceed with conversational execution.\n"
                "Memory Profile: {{memories}}",
                "1.0.0"
            )
        }

    def get_prompt_value(self, key: str, variables: Dict[str, Any]) -> str:
        """Fetch, render and return the compiled prompt template."""
        template = self._templates.get(key, self._templates["system_agent_default"])
        # Complete missing mappings gracefully
        required_vars = ["context", "memories", "documents", "user_intent", "input_plan", "approved_plan", "rag_chunks", "system_state"]
        filled_vars = {**{v: "" for v in required_vars}, **variables}
        return template.render(filled_vars)

    def get_template_version(self, key: str) -> str:
        return self._templates.get(key, self._templates["system_agent_default"]).version

    def register_template(self, key: str, template: str, version: str) -> None:
        """Enable dynamic runtime insertion or overriding of versions."""
        self._templates[key] = VersionedPrompt(template, version)

    def get_all_templates(self) -> Dict[str, Dict[str, str]]:
        return {
            k: {"template": t._template, "version": t._version}
            for k, t in self._templates.items()
        }
