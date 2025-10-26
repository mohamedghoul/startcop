import * as React from "react"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

interface Step {
  id: string
  title: string
  description?: string
}

interface StepperProps {
  steps: Step[]
  currentStep: number
  orientation?: "horizontal" | "vertical"
  className?: string
}

export function Stepper({
  steps,
  currentStep,
  orientation = "horizontal",
  className,
}: StepperProps) {
  return (
    <div
      className={cn(
        "flex",
        orientation === "horizontal"
          ? "flex-row items-start justify-between"
          : "flex-col space-y-4",
        className
      )}
      role="list"
      aria-label="Progress"
    >
      {steps.map((step, index) => {
        const isCompleted = index < currentStep
        const isCurrent = index === currentStep
        const isUpcoming = index > currentStep

        return (
          <div
            key={step.id}
            className={cn(
              "flex items-start",
              orientation === "horizontal" ? "flex-1" : "flex-row"
            )}
            role="listitem"
          >
            <div className="flex items-center">
              <div
                className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors",
                  isCompleted &&
                    "border-primary bg-primary text-primary-foreground",
                  isCurrent &&
                    "border-primary bg-background text-primary",
                  isUpcoming && "border-muted bg-background text-muted-foreground"
                )}
                aria-current={isCurrent ? "step" : undefined}
              >
                {isCompleted ? (
                  <Check className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              {orientation === "horizontal" && index < steps.length - 1 && (
                <div
                  className={cn(
                    "ml-4 h-0.5 w-full transition-colors",
                    isCompleted ? "bg-primary" : "bg-muted"
                  )}
                  aria-hidden="true"
                />
              )}
            </div>
            <div
              className={cn(
                "ml-4 flex flex-col",
                orientation === "horizontal" ? "hidden lg:flex" : "flex"
              )}
            >
              <span
                className={cn(
                  "text-sm font-medium",
                  isCurrent && "text-foreground",
                  (isCompleted || isUpcoming) && "text-muted-foreground"
                )}
              >
                {step.title}
              </span>
              {step.description && orientation === "vertical" && (
                <span className="text-sm text-muted-foreground">
                  {step.description}
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

