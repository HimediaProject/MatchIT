import React, { useEffect, useRef, useState } from 'react'
import { skillsApi } from '../services/apiService'

type Props = {
  onChange?: (skills: string[]) => void
  initial?: string[]
}

const SkillSelector: React.FC<Props> = ({ onChange, initial = [] }) => {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [selected, setSelected] = useState<string[]>(initial)
  const timerRef = useRef<number | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    onChange?.(selected)
  }, [selected, onChange])

  useEffect(() => {
    if (!open) return
    inputRef.current?.focus()
  }, [open])

  useEffect(() => {
    // debounce
    if (!query) {
      setSuggestions([])
      return
    }
    if (timerRef.current) window.clearTimeout(timerRef.current)
    timerRef.current = window.setTimeout(async () => {
      try {
        const res = await skillsApi.autocomplete(query)
        if (res && Array.isArray(res.skills)) setSuggestions(res.skills)
        else setSuggestions([])
      } catch (e) {
        setSuggestions([])
      }
    }, 250)
    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current)
    }
  }, [query])

  function addSkill(skill: string) {
    const trimmed = skill.trim()
    if (!trimmed) return
    if (selected.includes(trimmed)) return
    setSelected((s) => [...s, trimmed])
    setQuery('')
    setSuggestions([])
    setOpen(false)
  }

  function removeSkill(skill: string) {
    setSelected((s) => s.filter((x) => x !== skill))
  }

  return (
    <div className="relative">
      <div className="flex flex-wrap items-center gap-2">
        {selected.map((s) => (
          <span
            key={s}
            className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-800"
          >
            {s}
            <button
              onClick={() => removeSkill(s)}
              className="ml-1 text-xs text-slate-500"
              aria-label={`remove ${s}`}
            >
              ×
            </button>
          </span>
        ))}

        {!open && (
          <button
            onClick={() => setOpen(true)}
            className="rounded-full border border-dashed border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 hover:border-primary-300 hover:text-primary-700"
          >
            +선택
          </button>
        )}
      </div>

      {open && (
        <div className="absolute left-0 z-20 mt-2 w-72 rounded-md border bg-white p-2 shadow-lg">
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                addSkill(query)
              } else if (e.key === 'Escape') {
                setOpen(false)
              }
            }}
            placeholder="스킬 입력 (예: React, Python)"
            className="w-full rounded-md border px-3 py-2 text-sm outline-none"
          />

          <div className="mt-2 max-h-40 overflow-auto">
            {suggestions.length > 0 ? (
              suggestions.map((s) => (
                <div
                  key={s}
                  onClick={() => addSkill(s)}
                  className="cursor-pointer rounded px-2 py-1 text-sm hover:bg-slate-100"
                >
                  {s}
                </div>
              ))
            ) : (
              query && (
                <div className="rounded px-2 py-1 text-sm text-slate-600">입력하신 '{query}'(으)로 추가하려면 Enter</div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default SkillSelector
