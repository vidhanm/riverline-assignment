export default function AudioPlayer({ audioPath }) {
  if (!audioPath) {
    return <span className="text-sm text-gray-400">No audio</span>;
  }

  // Ensure proper URL format
  const audioUrl = audioPath.startsWith('http')
    ? audioPath
    : `http://localhost:8000/${audioPath}`;

  return (
    <audio controls className="w-full max-w-md">
      <source src={audioUrl} type="audio/mpeg" />
      Your browser does not support audio playback.
    </audio>
  );
}
