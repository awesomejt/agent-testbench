import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />)
    expect(container).toBeTruthy()
  })

  it('mounts a root element', () => {
    render(<App />)
    expect(document.body.firstChild).toBeTruthy()
  })
})
