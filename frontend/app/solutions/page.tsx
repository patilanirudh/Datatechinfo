import ApiErrorNotice from "@/components/ApiErrorNotice";
import { ApiError, getSolutions } from "@/lib/api";
import type { Solutions, SolutionGroup } from "@/lib/types";

export const dynamic = "force-dynamic";

async function safeLoad<T>(loader: () => Promise<T>): Promise<T | null> {
  try {
    return await loader();
  } catch (err) {
    if (err instanceof ApiError || err instanceof TypeError) return null;
    throw err;
  }
}

function SolutionSection({ group }: { group: SolutionGroup }) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-zinc-950 dark:text-zinc-50">{group.label}</h2>
      <div className="mt-3 flex flex-col gap-3">
        {group.items.map((item) => (
          <div
            key={item.title}
            className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
          >
            <p className="font-medium text-zinc-900 dark:text-zinc-100">{item.title}</p>
            <p className="mt-1 text-sm leading-6 text-zinc-600 dark:text-zinc-400">
              {item.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default async function SolutionsPage() {
  const solutions = await safeLoad<Solutions>(getSolutions);

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">Solutions</h1>
        <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
          What you can do with this dashboard today, and the systemic fixes that would need a transit
          authority or large employer to implement.
        </p>
      </div>

      {solutions === null ? (
        <ApiErrorNotice />
      ) : (
        <>
          <SolutionSection group={solutions.personal} />
          <SolutionSection group={solutions.systemic} />
        </>
      )}
    </div>
  );
}
