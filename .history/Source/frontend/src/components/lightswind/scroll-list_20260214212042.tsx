"use client";
import React, { useRef, useEffect, useState, useMemo } from "react";
import { motion, useScroll, Variants } from "framer-motion";

// Define the props for the ScrollList component
interface ScrollListProps<T> {
  data: T[]; // The array of data items to display
  renderItem: (item: T, index: number) => React.ReactNode; // Function to render each item's content
  itemHeight?: number; // Optional: Fixed height for each item in pixels. If not provided, items will auto-size based on content.
  itemSpacing?: number; // Optional: Spacing between items in pixels. Defaults to 1rem (16px).
  minItemHeight?: number; // Optional: Minimum height for each item in pixels.
}

// Function to generate a random gradient
const generateRandomGradient = (): string => {
  // Predefined beautiful gradient color combinations
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    'linear-gradient(135deg, #ff8a80 0%, #ea6100 100%)',
    'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
    'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)',
    'linear-gradient(135deg, #ff6e7f 0%, #bfe9ff 100%)',
    'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)',
    'linear-gradient(135deg, #fad961 0%, #f76b1c 100%)',
    'linear-gradient(135deg, #5ee7df 0%, #b490ca 100%)',
    'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
    'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
    'linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%)',
    'linear-gradient(135deg, #ee9ca7 0%, #ffdde1 100%)',
  ];

  // Return a random gradient from the array
  return gradients[Math.floor(Math.random() * gradients.length)];
};

const ScrollList = <T,>({
  data,
  renderItem,
  itemHeight, // No default - allows auto-sizing
  itemSpacing = 16, // Default spacing between items
  minItemHeight, // Optional minimum height
}: ScrollListProps<T>) => {
  // useRef to get a reference to the scrollable div element
  const listRef = useRef<HTMLDivElement>(null);
  // useState to keep track of the index of the currently focused item
  const [focusedIndex, setFocusedIndex] = useState<number>(0);

  // Generate random gradients for each item (memoized to keep them consistent)
  const itemGradients = useMemo(() => {
    return data.map(() => generateRandomGradient());
  }, [data.length]); // Only regenerate if data length changes

  // useScroll hook from Framer Motion to track scroll progress (can be used for additional animations)
  const { scrollYProgress } = useScroll({ container: listRef });

  useEffect(() => {
    const updateFocusedItem = () => {
      if (!listRef.current) return;

      const container = listRef.current;
      // Get all direct children (the motion.div items)
      const children = Array.from(container.children) as HTMLDivElement[];
      const scrollTop = container.scrollTop; // Current vertical scroll position
      const containerCenter = container.clientHeight / 2; // Vertical center of the container

      let closestItemIndex = 0;
      let minDistanceToCenter = Infinity; // Initialize with a very large number

      // Iterate over each child item to find the one closest to the center
      children.forEach((child, index) => {
        const itemTop = child.offsetTop; // Top position of the item relative to its parent
        const actualItemHeight = child.offsetHeight; // Actual rendered height of the item
        const itemCenter = itemTop + actualItemHeight / 2; // Vertical center of the item

        // Calculate the distance from the item's center to the container's center, adjusted for scroll
        const distanceToCenter = Math.abs(
          itemCenter - scrollTop - containerCenter
        );

        // If this item is closer to the center than the previous closest
        if (distanceToCenter < minDistanceToCenter) {
          minDistanceToCenter = distanceToCenter;
          closestItemIndex = index;
        }
      });

      // Update the focused index state
      setFocusedIndex(closestItemIndex);
    };

    // Call immediately on mount to set initial focused item
    updateFocusedItem();

    // Add scroll event listener to update focused item on scroll
    const listElement = listRef.current;
    if (listElement) {
      listElement.addEventListener("scroll", updateFocusedItem);
    }

    // Cleanup function: remove the event listener when the component unmounts
    return () => {
      if (listElement) {
        listElement.removeEventListener("scroll", updateFocusedItem);
      }
    };
  }, [data, itemHeight]); // Dependencies: Re-run effect if data or itemHeight changes

  // Framer Motion Variants for defining animation states for each item
  const itemVariants: Variants = {
    hidden: {
      opacity: 0,
      scale: 0.7,
      transition: { duration: 0.35, ease: "easeOut" },
    },
    focused: {
      opacity: 1,
      scale: 1,
      zIndex: 10,
      transition: { duration: 0.35, ease: "easeOut" },
    },
    next: {
      opacity: 1,
      scale: 0.95,
      zIndex: 5,
      transition: { duration: 0.35, ease: "easeOut" },
    },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.35, ease: "easeOut" },
    },
  };

  return (
    <div
      ref={listRef}
      // Tailwind CSS classes for styling: hidden scrollbar, centered horizontally, full width
      className="scroll-list__wrp scrollbar-hidden mx-auto w-full"
      // Inline style for fixed height and scrollability of the main container
      style={{ height: "600px", overflowY: "auto" }}
    >
      {data.map((item, index) => {
        let variant = "hidden"; // Default variant

        // Determine the animation variant based on the item's position relative to the focused item
        if (index === focusedIndex) {
          variant = "focused"; // The currently focused item
        } else if (index === focusedIndex + 1) {
          variant = "next"; // The item immediately following the focused one
        } else {
          // Items within a certain range (2 items above/below) of the focused item are visible
          const isWithinVisibleRange = Math.abs(index - focusedIndex) <= 2;
          if (isWithinVisibleRange) {
            variant = "visible";
          }
        }

        return (
          <motion.div
            key={index} // Unique key for React list rendering
            className="scroll-list__item mx-auto max-w-3xl" // Centered with max width
            variants={itemVariants} // Apply defined animation variants
            initial="hidden" // Initial animation state
            animate={variant} // Animate to this variant based on scroll position
            // Set the height and spacing of each individual item
            style={{
              height: itemHeight ? `${itemHeight}px` : "auto",
              minHeight: minItemHeight ? `${minItemHeight}px` : undefined,
              marginBottom: index < data.length - 1 ? `${itemSpacing}px` : 0, // Add spacing between items
              marginTop: index === 0 ? 0 : undefined, // No top margin for first item
            }}
          >
            {renderItem(item, index)}
          </motion.div>
        );
      })}
    </div>
  );
};

export default ScrollList;
