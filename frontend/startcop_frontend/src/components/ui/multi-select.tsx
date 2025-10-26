import * as React from "react"
import { Check, X, Search } from "lucide-react"
import { cn } from "@/lib/utils"
import { Input } from "./input"
import { Button } from "./button"
import { Card } from "./card"

export interface SelectOption {
  value: string
  label: string
}

interface MultiSelectProps {
  options: SelectOption[]
  selected: string[]
  onChange: (selected: string[]) => void
  placeholder?: string
  searchable?: boolean
  disabled?: boolean
  className?: string
}

export function MultiSelect({
  options,
  selected,
  onChange,
  placeholder = "Select items...",
  searchable = true,
  disabled = false,
  className,
}: MultiSelectProps) {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [isOpen, setIsOpen] = React.useState(false)
  const containerRef = React.useRef<HTMLDivElement>(null)

  const filteredOptions = React.useMemo(() => {
    if (!searchQuery) return options
    const query = searchQuery.toLowerCase()
    return options.filter((opt) =>
      opt.label.toLowerCase().includes(query)
    )
  }, [options, searchQuery])

  const selectedOptions = React.useMemo(
    () => options.filter((opt) => selected.includes(opt.value)),
    [options, selected]
  )

  const toggleOption = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value))
    } else {
      onChange([...selected, value])
    }
  }

  const removeOption = (value: string) => {
    onChange(selected.filter((v) => v !== value))
  }

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div
        className={cn(
          "flex min-h-10 w-full flex-wrap gap-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
          disabled && "cursor-not-allowed opacity-50",
          !disabled && "cursor-text"
        )}
        onClick={() => !disabled && setIsOpen(true)}
      >
        {selectedOptions.length === 0 && (
          <span className="text-muted-foreground">{placeholder}</span>
        )}
        {selectedOptions.map((opt) => (
          <span
            key={opt.value}
            className="inline-flex items-center gap-1 rounded bg-primary px-2 py-0.5 text-xs text-primary-foreground"
          >
            {opt.label}
            <button
              type="button"
              className="ml-1 rounded-sm hover:bg-primary-foreground/20"
              onClick={(e) => {
                e.stopPropagation()
                removeOption(opt.value)
              }}
              disabled={disabled}
              aria-label={`Remove ${opt.label}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>

      {isOpen && !disabled && (
        <Card className="absolute z-50 mt-2 w-full p-2 shadow-lg">
          {searchable && (
            <div className="relative mb-2">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
                autoFocus
              />
            </div>
          )}
          <div className="max-h-60 overflow-y-auto">
            {filteredOptions.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                No results found
              </p>
            ) : (
              <div className="space-y-1">
                {filteredOptions.map((option) => {
                  const isSelected = selected.includes(option.value)
                  return (
                    <button
                      key={option.value}
                      type="button"
                      className={cn(
                        "flex w-full items-center justify-between rounded-sm px-2 py-1.5 text-sm hover:bg-accent",
                        isSelected && "bg-accent"
                      )}
                      onClick={() => toggleOption(option.value)}
                    >
                      <span>{option.label}</span>
                      {isSelected && (
                        <Check className="h-4 w-4 text-primary" aria-hidden="true" />
                      )}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}

