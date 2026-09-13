import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ApiErrorNotice from "@/components/ApiErrorNotice";
import { ApiError, getCaseStudy } from "@/lib/api";
import type { CaseStudy } from "@/lib/types";

export const dynamic = "force-dynamic";

async function safeLoad<T>(loader: () => Promise<T>): Promise<T | null> {
  try {
    return await loader();
  } catch (err) {
    if (err instanceof ApiError || err instanceof TypeError) return null;
    throw err;
  }
}

interface ParsedCaseStudy {
  title: string | null;
  date: string | null;
  body: string;
}

function parseFrontmatter(markdown: string): ParsedCaseStudy {
  const match = markdown.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) return { title: null, date: null, body: markdown };

  const fields: Record<string, string> = {};
  for (const line of match[1].split("\n")) {
    const fieldMatch = line.match(/^(\w+):\s*(.*)$/);
    if (fieldMatch) fields[fieldMatch[1]] = fieldMatch[2].replace(/^"(.*)"$/, "$1");
  }

  return {
    title: fields.title ?? null,
    date: fields.date ?? null,
    body: markdown.slice(match[0].length),
  };
}

export default async function CaseStudyPage() {
  const caseStudy = await safeLoad<CaseStudy>(getCaseStudy);

  if (caseStudy === null) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">Case study</h1>
        <ApiErrorNotice />
      </div>
    );
  }

  const { title, date, body } = parseFrontmatter(caseStudy.markdown);

  return (
    <div className="flex flex-col gap-1">
      {title && (
        <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">{title}</h1>
      )}
      {date && <p className="text-sm text-zinc-500 dark:text-zinc-500">{date}</p>}
      <article
        className="
          mt-4 max-w-3xl
          [&_a]:underline [&_a]:underline-offset-2
          [&_h2]:mt-8 [&_h2]:text-lg [&_h2]:font-semibold
          [&_hr]:my-8 [&_hr]:border-zinc-200 dark:[&_hr]:border-zinc-800
          [&_li]:mt-1
          [&_ol]:mt-3 [&_ol]:list-decimal [&_ol]:pl-5
          [&_p]:mt-3 [&_p]:leading-7
          [&_ul]:mt-3 [&_ul]:list-disc [&_ul]:pl-5
          text-zinc-800 dark:text-zinc-200
        "
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{body}</ReactMarkdown>
      </article>
    </div>
  );
}
