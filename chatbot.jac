import from byllm.lib { Model }

glob llm = Model(model_name="gemini/gemini-2.0-flash");

#  Conversation node 
node ChatHistory {
    has messages: list = [];
}

# --- LLM function: accept prompt + history and return string ---
def chat_with_ai(prompt: str, history: list) -> str by llm(
    system_prompt="You are a helpful AI assistant that keeps conversation context."
);

#  API Walker 
walker ChatAPI {
    has prompt: str;
    has session: ChatHistory = None;

    obj __specs__ {
        static has auth: bool = False;
    }

    can run with `root entry {
        # Ensure prompt is a string
        if  self.prompt == None {
            report {"error": "Missing prompt"} ;
            disengage;
        }

        # Find or create ChatHistory node (persisted under root)
        if self.session == None {
            hist_nodes = [root ->:ChatHistory:->];
            if len(hist_nodes) == 0 {
                # correct spawn syntax (returns node object)
                session = spawn ChatHistory;
                # link it to root so future calls can find it
                root +>:ChatHistory:+> session;
                self.session = session;
            } else {
                self.session = hist_nodes[0];
            }
        }

        # Ensure session.messages is a list of dicts with string contents
        if self.session.messages == None {
            self.session.messages = [];
        }

        # Build history for the LLM: convert stored items to strings (defensive)
        hist = [];
        for m in self.session.messages {
            # Only include entries that are dicts and have 'role' and 'content' as strings
            if typeof(m) == "dict" and ("role" in m) and ("content" in m) {
                # coerce to string to avoid non-serializable values
                hist.append({"role": str(m["role"]), "content": str(m["content"])});
            }
        }

        # Append incoming user message to history (use string cast)
        hist.append({"role": "user", "content": str(self.prompt)});

        # Call the LLM helper passing prompt + history
        # Expectation: chat_with_ai returns a plain string reply
        reply = chat_with_ai(prompt=self.prompt, history=hist);

        # Defensive: coerce reply to string (avoid non-serializable)
        reply_text = str(reply);

        # Persist both messages in session
        self.session.messages.append({"role": "user", "content": str(self.prompt)});
        self.session.messages.append({"role": "assistant", "content": reply_text});

        # Return a JSON-serializable object
        report {
            "reply": reply_text,
            "conversation": self.session.messages
        };
    }
}
