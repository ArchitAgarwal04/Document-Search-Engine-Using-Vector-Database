import time
from typing import List, Optional
from app.config import settings
from app.search.retriever import semantic_search
from app.rag.prompts import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_TEMPLATE,
    CHAT_HISTORY_TEMPLATE,
    format_context_block,
    format_conversation_history,
)

# ─── Singleton clients ────────────────────────────────────────────────────────
_gemini_client = None
_groq_client = None


def get_gemini_client():
    """Returns the singleton Google Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=settings.gemini_api_key)
        print(f"[RAG] Gemini client ready — model: {settings.gemini_model}")
    return _gemini_client


def get_groq_client():
    """Returns the singleton Groq client."""
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=settings.groq_api_key)
        print(f"[RAG] Groq client ready — model: {settings.groq_model}")
    return _groq_client


# ─── Provider call helpers ────────────────────────────────────────────────────

def _call_gemini(prompt: str, max_retries: int = 3) -> str:
    """Call Gemini with exponential backoff on 429 errors (5s → 10s → 20s)."""
    from google.genai import types
    client = get_gemini_client()
    wait = 5

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=RAG_SYSTEM_PROMPT,
                    temperature=0.2,
                    max_output_tokens=1024,
                ),
            )
            return response.text.strip() if response.text else "No response generated."

        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                if attempt < max_retries:
                    print(f"[RAG][Gemini] Rate limit hit (attempt {attempt}/{max_retries}). Retrying in {wait}s...")
                    time.sleep(wait)
                    wait *= 2
                    continue
                return (
                    "The Gemini AI service is rate-limited (free tier quota exhausted). "
                    "Please wait 1-2 minutes or switch to Groq by setting LLM_PROVIDER=groq in your .env file."
                )
            print(f"[RAG][Gemini] Error: {err}")
            return f"Error generating response: {err[:300]}"

    return "No response generated."


def _call_groq(prompt: str, max_retries: int = 3) -> str:
    """Call Groq with retry on transient errors. Groq free tier: 6000 RPM."""
    client = get_groq_client()
    wait = 2

    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1024,
            )
            return completion.choices[0].message.content.strip()

        except Exception as e:
            err = str(e)
            # 429 on Groq is extremely rare but handle it anyway
            if "429" in err or "rate" in err.lower():
                if attempt < max_retries:
                    print(f"[RAG][Groq] Rate limit hit (attempt {attempt}/{max_retries}). Retrying in {wait}s...")
                    time.sleep(wait)
                    wait *= 2
                    continue
                return (
                    "The Groq AI service is temporarily rate-limited. "
                    "Please wait a moment and try again."
                )
            print(f"[RAG][Groq] Error: {err}")
            return f"Error generating response: {err[:300]}"

    return "No response generated."


def _call_llm(prompt: str) -> str:
    """
    Route the LLM call to the configured provider.
    Set LLM_PROVIDER in .env to 'gemini' or 'groq'.
    """
    provider = settings.llm_provider.lower()
    print(f"[RAG] Using LLM provider: {provider}")

    if provider == "groq":
        return _call_groq(prompt)
    elif provider == "gemini":
        return _call_gemini(prompt)
    else:
        return f"Unknown LLM provider '{provider}'. Set LLM_PROVIDER to 'gemini' or 'groq' in .env"


# ─── Main RAG pipeline ────────────────────────────────────────────────────────

def run_rag_pipeline(
    question: str,
    conversation_history: Optional[List] = None,
    document_ids: Optional[List[int]] = None,
) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from ChromaDB
    2. Check similarity threshold (avoid hallucination on irrelevant queries)
    3. Format context + conversation history into a prompt
    4. Send to configured LLM (Groq or Gemini) with automatic retry
    5. Return answer + source citations
    """
    start_time = time.time()

    # Step 1: Retrieve relevant chunks
    search_result = semantic_search(
        query=question,
        top_k=settings.top_k_results,
        document_ids=document_ids,
    )
    chunks = search_result["results"]

    # Step 2: No results → bail early
    if not chunks:
        elapsed = round((time.time() - start_time) * 1000, 2)
        return {
            "answer": (
                "I couldn't find relevant information in the uploaded documents to answer this question. "
                "Please try rephrasing your question or upload documents related to your topic."
            ),
            "sources": [],
            "has_answer": False,
            "response_time_ms": elapsed,
        }

    # Step 3: Format context block
    context_text = format_context_block(chunks)

    # Step 4: Build prompt (with or without conversation history)
    if conversation_history:
        history_text = format_conversation_history(conversation_history)
        prompt = CHAT_HISTORY_TEMPLATE.format(
            history=history_text,
            context=context_text,
            question=question,
        )
    else:
        prompt = RAG_USER_TEMPLATE.format(
            context=context_text,
            question=question,
        )

    # Step 5: Call the configured LLM
    answer = _call_llm(prompt)

    # Step 6: Build source citations (top 3 chunks)
    sources = [
        {
            "document_name": chunk["document_name"],
            "document_id": chunk["document_id"],
            "page_number": chunk.get("page_number"),
            "chunk_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
            "similarity_score": chunk["similarity_score"],
        }
        for chunk in chunks[:3]
    ]

    elapsed = round((time.time() - start_time) * 1000, 2)

    return {
        "answer": answer,
        "sources": sources,
        "has_answer": True,
        "response_time_ms": elapsed,
    }
