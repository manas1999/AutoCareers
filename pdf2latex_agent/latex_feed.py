import openai
from pathlib import Path

from llama_index.llms.together import TogetherLLM

CONFIG_PATH = Path(__file__).parent / "config.yaml"

def feed_latex_to_llm(latex_content: str,config_data: str) -> str:
    """
    Reads config.yaml, checks if we should call Together or OpenAI,
    and returns the final string response.
    """


    # If config_data says 'use_together: true', use the Together API; otherwise use OpenAI
    use_together = config_data.get("use_together", False)

    if use_together:
        # Call the Together function
        return feed_latex_to_llm_via_together(latex_content, config_data)
    else:
        # Call the OpenAI function
        return feed_latex_to_llm_via_openai(latex_content, config_data)

def feed_latex_to_llm_via_openai(latex_content: str, config_data: dict) -> str:
    """
    Feeds LaTeX content to OpenAI's ChatCompletion.
    """
    openai.api_key = config_data.get("openai_api_key", "YOUR_OPENAI_KEY_HERE")
    agent_config = config_data.get("agents", {}).get("pdf2latex", {})

    model_name = agent_config.get("default_model", "gpt-3.5-turbo")
    system_prompt = agent_config.get("system_prompt", "")

    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Here is a LaTeX document:\n\n{latex_content}\n\nPlease analyze it."}
        ]
    )

    return response.choices[0].message.content

def feed_latex_to_llm_via_together(latex_content: str,config_data: str) -> str:
    """
    Feeds LaTeX content to a Together LLM, streaming tokens in real-time.
    Collects them into a single string response.
    """
    together_api_key = config_data.get("TOGETHER_API_KEY", "YOUR_OPENAI_KEY_HERE")
    agent_config = config_data.get("agents", {}).get("pdf2latex", {})
    together_model = agent_config.get("together_model", "meta-llama/Llama-2-70B-Instruct")
    user_prompt = agent_config.get("user_prompt")

    messages = [
        {"role": "system", "content": agent_config.get("system_prompt", "")},
        {"role": "user",   "content": f"Here is a LaTeX document:\n\n{latex_content}\n\n{user_prompt}"}
    ]

    user_text = "\n\n".join(m["content"] for m in messages if m["role"] != "system")
    system_text = next((m["content"] for m in messages if m["role"] == "system"), "")

    client = TogetherLLM(
            api_key=together_api_key,
            model=together_model,
            temperature=0.7
        )

    prompt_text = f"[System]\n{system_text}\n\n[User]\n{user_text}"
    
    response = client.complete(
        prompt_text
    )

    return response
