interface ErrorMessageProps {
  message: string
  onRetry?: () => void
}

export default function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="rounded-lg border border-red-800 bg-red-950 p-4 text-center">
      <p className="text-sm text-red-300">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 rounded bg-red-800 px-4 py-1.5 text-xs font-medium text-red-200 transition-colors hover:bg-red-700"
        >
          Retry
        </button>
      )}
    </div>
  )
}
