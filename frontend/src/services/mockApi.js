/**
 * Mock API latency simulator helper.
 * Generates a random response delay between 300ms and 800ms.
 * 
 * @param {number} [min=300] Minimum delay in milliseconds
 * @param {number} [max=800] Maximum delay in milliseconds
 * @returns {Promise<void>}
 */
export const delay = (min = 300, max = 800) => {
  const ms = Math.floor(Math.random() * (max - min + 1) + min)
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export default { delay }
