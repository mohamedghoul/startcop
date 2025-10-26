import { useState, useEffect, useCallback, useRef } from 'react';

interface UseLazyEffectOptions {
  delay?: number;
  triggerOnHover?: boolean;
  triggerOnClick?: boolean;
  triggerOnScroll?: boolean;
  threshold?: number;
}

/**
 * Hook for lazy loading heavy effects based on user interaction
 * Delays expensive operations until user shows interest
 */
export const useLazyEffect = (
  effect: () => void | (() => void),
  deps: React.DependencyList = [],
  options: UseLazyEffectOptions = {}
) => {
  const {
    delay = 0,
    triggerOnHover = false,
    triggerOnClick = false,
    triggerOnScroll = false,
    threshold = 0.1
  } = options;

  const [isTriggered, setIsTriggered] = useState<boolean>(false);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);
  const elementRef = useRef<HTMLElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const triggerEffect = useCallback(() => {
    if (isTriggered) return;
    
    setIsTriggered(true);
    
    if (delay > 0) {
      timeoutRef.current = setTimeout(() => {
        setIsLoaded(true);
        effect();
      }, delay);
    } else {
      setIsLoaded(true);
      effect();
    }
  }, [isTriggered, delay, effect]);

  const handleHover = useCallback(() => {
    if (triggerOnHover) {
      triggerEffect();
    }
  }, [triggerOnHover, triggerEffect]);

  const handleClick = useCallback(() => {
    if (triggerOnClick) {
      triggerEffect();
    }
  }, [triggerOnClick, triggerEffect]);

  const handleScroll = useCallback(() => {
    if (triggerOnScroll && elementRef.current) {
      const rect = elementRef.current.getBoundingClientRect();
      const isVisible = rect.top < window.innerHeight * (1 - threshold);
      
      if (isVisible) {
        triggerEffect();
      }
    }
  }, [triggerOnScroll, threshold, triggerEffect]);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    if (triggerOnHover) {
      element.addEventListener('mouseenter', handleHover);
    }
    
    if (triggerOnClick) {
      element.addEventListener('click', handleClick);
    }
    
    if (triggerOnScroll) {
      window.addEventListener('scroll', handleScroll);
      // Check initial position
      handleScroll();
    }

    return () => {
      if (triggerOnHover) {
        element.removeEventListener('mouseenter', handleHover);
      }
      
      if (triggerOnClick) {
        element.removeEventListener('click', handleClick);
      }
      
      if (triggerOnScroll) {
        window.removeEventListener('scroll', handleScroll);
      }
      
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [handleHover, handleClick, handleScroll, triggerOnHover, triggerOnClick, triggerOnScroll]);

  return {
    elementRef,
    isTriggered,
    isLoaded,
    triggerEffect,
  };
};

/**
 * Hook for progressive enhancement of visual effects
 * Loads basic effects immediately, enhanced effects on interaction
 */
export const useProgressiveEnhancement = (
  basicEffect: () => void,
  enhancedEffect: () => void,
  options: UseLazyEffectOptions = {}
) => {
  const { elementRef, isLoaded, triggerEffect } = useLazyEffect(
    enhancedEffect,
    [],
    options
  );

  useEffect(() => {
    // Load basic effect immediately
    basicEffect();
  }, [basicEffect]);

  return {
    elementRef,
    isLoaded,
    triggerEffect,
  };
};
