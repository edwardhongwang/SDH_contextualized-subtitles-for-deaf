const get_sum = async (root, numbers=[]) => {
  const all = numbers.join("+");
  return (
    await (await fetch(`${root}/sum/${all}`)).text()
  )
}

export { get_sum }
