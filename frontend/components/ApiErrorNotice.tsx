export default function ApiErrorNotice({ message }: { message?: string }) {
  return (
    <div className="rounded-lg border border-dashed border-zinc-300 bg-zinc-50 p-6 text-sm text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900/50 dark:text-zinc-400">
      <p className="font-medium text-zinc-800 dark:text-zinc-200">Couldn&apos;t reach the API</p>
      <p className="mt-1">
        {message ??
          "The backend isn't responding. Make sure it's running and NEXT_PUBLIC_API_BASE_URL points at it."}
      </p>
    </div>
  );
}
