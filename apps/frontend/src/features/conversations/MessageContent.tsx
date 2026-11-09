import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

import type { Schemas } from "@/services/api/client";

/** Conteúdo de uma mensagem. Respostas do assistente são Markdown; HTML bruto não é renderizado. */
export function MessageContent({
  role,
  content,
}: {
  role: Schemas["Message"]["role"];
  content: string;
}) {
  if (role === "user") return <p className="message-text">{content}</p>;
  return (
    <div className="message-markdown">
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: (props) => <a {...props} target="_blank" rel="noreferrer" />,
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}
