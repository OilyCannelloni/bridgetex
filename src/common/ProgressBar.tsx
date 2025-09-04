type ProgressProps = {
  value: number | null;
};

export default function ProgressBar({ value }: ProgressProps) {
  return (
    <div className="relative h-4 m-4 bg-gray-200 rounded overflow-hidden">
      {value !== null ? (
        <div
          className="h-full bg-green-500 transition-all duration-300"
          style={{ width: `${value}%` }}
        />
      ) : (
        <div className="progress-indeterminate" />
      )}
    </div>
  );
}