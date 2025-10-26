import { useState, useEffect } from 'react';

/**
 * Custom hook to detect user's motion preference
 * Respects prefers-reduced-motion media query for accessibility
 */
export const useReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);

  useEffect(() => {
    // Check if the media query is supported
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    // Set initial value
    setPrefersReducedMotion(mediaQuery.matches);

    // Create event listener
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    // Add listener
    mediaQuery.addEventListener('change', handleChange);

    // Cleanup
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return prefersReducedMotion;
};

/**
 * Hook to get animation duration based on reduced motion preference
 * @param normalDuration - Normal animation duration in seconds
 * @param reducedDuration - Reduced animation duration in seconds (default: 0.01)
 */
export const useAnimationDuration = (
  normalDuration: number,
  reducedDuration: number = 0.01
): number => {
  const prefersReducedMotion = useReducedMotion();
  return prefersReducedMotion ? reducedDuration : normalDuration;
};

/**
 * Hook to get animation iteration count based on reduced motion preference
 * @param normalIterations - Normal iteration count
 * @param reducedIterations - Reduced iteration count (default: 1)
 */
export const useAnimationIterations = (
  normalIterations: number | 'infinite',
  reducedIterations: number = 1
): number | 'infinite' => {
  const prefersReducedMotion = useReducedMotion();
  return prefersReducedMotion ? reducedIterations : normalIterations;
};
