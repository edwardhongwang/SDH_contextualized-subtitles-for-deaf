const storeSoundCounts = (listing, sounds) => {
  const key = `${listing}/sounds/counts`;
  const sound_counts = JSON.parse(
    localStorage.getItem(key) || '{}'
  );
  const n = sound_counts["n"] || 0;
  sound_counts["n"] = n + 1;
  sounds.forEach(sound => {
    const counts = sound_counts[sound] || 0;
    sound_counts[sound] = counts + 1;
  });
  localStorage.setItem(key, JSON.stringify(
    sound_counts
  ));
  return sound_counts;
}

const clearSoundCounts = (listing) => {
  const key = `${listing}/sounds/counts`;
  localStorage.removeItem(key)
}

const getSoundCounts = (listing) => {
  const key = `${listing}/sounds/counts`;
  return localStorage.getItem(key);
}

export {
  storeSoundCounts, clearSoundCounts, getSoundCounts
}
