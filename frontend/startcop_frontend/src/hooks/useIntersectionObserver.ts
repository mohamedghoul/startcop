import { useEffect, useRef, useState, useCallback } from 'react';

interface UseIntersectionObserverOptions {
  threshold?: number | number[];
  rootMargin?: string;
  freezeOnceVisible?: boolean;
}

/**
 * Custom hook for IntersectionObserver to optimize performance
 * Pauses animations when elements are off-screen
 */
export const useIntersectionObserver = (
  options: UseIntersectionObserverOptions = {}
) => {
  const {
    threshold = 0.1,
    rootMargin = '0px',
    freezeOnceVisible = false
  } = options;

  const [isIntersecting, setIsIntersecting] = useState<boolean>(false);
  const [hasIntersected, setHasIntersected] = useState<boolean>(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      const isVisible = entry.isIntersecting;
      
      setIsIntersecting(isVisible);
      
      if (isVisible && !hasIntersected) {
        setHasIntersected(true);
      }
    },
    [hasIntersected]
  );

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(handleIntersection, {
      threshold,
      rootMargin,
    });

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [handleIntersection, threshold, rootMargin]);

  // Return whether animations should be active
  const shouldAnimate = freezeOnceVisible ? hasIntersected : isIntersecting;

  return {
    elementRef,
    isIntersecting,
    hasIntersected,
    shouldAnimate,
  };
};

/**
 * Hook specifically for animation control based on visibility
 */
export const useAnimationControl = (
  options: UseIntersectionObserverOptions = {}
) => {
  const { elementRef, shouldAnimate } = useIntersectionObserver(options);
  
  return {
    elementRef,
    shouldAnimate,
    // Helper to conditionally apply animation classes
    getAnimationClass: (baseClass: string, animationClass: string) => 
      shouldAnimate ? `${baseClass} ${animationClass}` : baseClass,
  };
};
