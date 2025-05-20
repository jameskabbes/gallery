export function generateRandomStringId(length = 10) {
  // Create a random string of specified length
  return [...Array(length)]
    .map(() => Math.random().toString(36)[2] || 0)
    .join('');
}
