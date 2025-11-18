import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO
import colorsys
from typing import List, Dict, Tuple
import math
import time


class AnimatedMoodBlobGenerator:
    """
    Creates Apple Pay-style animated mood blobs that evolve over time.
    Each user has ONE blob that morphs and changes colors based on emotional evolution.
    """
    
    def __init__(self, size: Tuple[int, int] = (1200, 1200)):
        self.size = size
        self.emotion_colors = {
            'joy': (255, 215, 0),      # Gold
            'sadness': (65, 105, 225),  # Royal Blue
            'anger': (220, 20, 60),     # Crimson
            'fear': (139, 0, 139),      # Dark Magenta
            'surprise': (255, 99, 71),  # Tomato
            'disgust': (85, 107, 47),   # Dark Olive Green
            'neutral': (128, 128, 128), # Gray
            'love': (255, 105, 180),    # Hot Pink
            'anxiety': (147, 112, 219), # Medium Purple
            'excitement': (255, 140, 0), # Dark Orange
        }
    
    def generate_evolution_blob(self, emotion_history: List[Dict], current_emotion: Dict, blob_state: Dict = None) -> BytesIO:
        """
        Generate an evolving blob based on emotional history.
        Each emotion now starts from a unique base shape (circle, heart, star, etc.).
        """
        # Load previous contour if available
        prev_points = None
        if blob_state:
            try:
                prev_img = Image.open(blob_state).convert('RGBA').resize(self.size)
                gray = np.array(prev_img.convert('L'))
                threshold = np.percentile(gray, 60)
                y, x = np.where(gray > threshold)
                if len(x) > 0:
                    coords = np.column_stack((x, y))
                    prev_points = [(int(px), int(py)) for px, py in coords[::len(coords)//360 or 1]]
            except Exception as e:
                print(f"⚠️ Failed to load previous blob state: {e}")
        
        # Create base image or load previous blob
        if blob_state:
            try:
                prev_img = Image.open(blob_state).convert('RGBA').resize(self.size)
                faded_prev = Image.blend(
                    prev_img,
                    Image.new('RGBA', self.size, (26, 26, 46, 255)),
                    alpha=0.15
                )
                image = faded_prev
            except Exception as e:
                print(f"⚠️ Could not load previous blob state: {e}")
                image = Image.new('RGBA', self.size, (26, 26, 46, 255))
        else:
            image = Image.new('RGBA', self.size, (26, 26, 46, 255))
        
        # Calculate evolving colors
        colors = self._calculate_color_evolution(emotion_history, current_emotion, blob_state)
        
        # Generate blob parameters
        blob_params = self._calculate_blob_parameters(current_emotion, emotion_history)
        # Add time-based evolution for a living effect
        time_factor = (time.time() % 60) / 60.0  # cycles every 60 seconds
        blob_params['seed'] += int(time_factor * 100)  # subtle dynamic evolution
        blob_params['variation'] = int(blob_params['variation'] * (0.9 + 0.2 * math.sin(time_factor * 2 * math.pi)))

        emotion_type = current_emotion.get('primary_emotion', 'neutral')
        self.current_emotion = emotion_type  # store for organic generation

        # --- 🟣 Base emotion shape ---
        base_points = self._get_emotion_shape_base(
            emotion=emotion_type,
            center=(self.size[0] // 2, self.size[1] // 2),
            radius=blob_params['radius'],
            points=360
        )

        # --- 🌊 Organic deformation ---
        new_points = self._generate_organic_blob(
            center=(self.size[0] // 2, self.size[1] // 2),
            base_radius=blob_params['radius'],
            variation=blob_params['variation'],
            seed=blob_params['seed']
        )

        # Interpolate shapes (smooth transition from last blob)
        if prev_points and len(prev_points) == len(new_points):
            new_points = self._interpolate_shapes(prev_points, new_points, alpha=0.35)

        # Draw and evolve
        self._draw_layered_blob(image, new_points, colors, blob_params)
        image = self._apply_glow_effect(image, colors[0])
        image = self._apply_smooth_blur(image)
        image = self._add_texture(image)
        
        buffer = BytesIO()
        image.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        return buffer


    def _interpolate_shapes(self, old_points: List[Tuple[int, int]], new_points: List[Tuple[int, int]], alpha: float = 0.5) -> List[Tuple[int, int]]:
        """
        Smoothly morph one shape into another by blending coordinates.
        alpha = 0 means use old shape fully,
        alpha = 1 means use new shape fully.
        """
        morphed = []
        for (x1, y1), (x2, y2) in zip(old_points, new_points):
            mx = int(x1 * (1 - alpha) + x2 * alpha)
            my = int(y1 * (1 - alpha) + y2 * alpha)
            morphed.append((mx, my))
        return morphed


    def _calculate_color_evolution(
        self, history: List[Dict], current: Dict, blob_state: str = None
    ) -> List[Tuple[int, int, int]]:
        """
        Calculate color palette based on emotional evolution.
        Creates smooth transitions between past and present emotional tones.
        """
        colors = []

        # --- Step 1: Determine current primary color
        primary_emotion = current.get('primary_emotion', 'neutral')
        primary_color = self.emotion_colors.get(primary_emotion, (128, 128, 128))

        # --- Step 2: Blend with last known emotion for smooth evolution
        if history:
            last_emotion = history[-1].get('primary_emotion', 'neutral')
            last_color = self.emotion_colors.get(last_emotion, (128, 128, 128))
            primary_color = self._blend_colors(last_color, primary_color, 0.6)

        # --- Step 3: Blend with previous blob hue (for continuity)
        if blob_state:
            try:
                from PIL import Image
                import numpy as np

                prev_img = Image.open(blob_state).convert("RGB")
                avg_color = tuple(np.mean(np.array(prev_img), axis=(0, 1)).astype(int))
                # Blend 40% with previous hue
                primary_color = self._blend_colors(avg_color, primary_color, 0.4)
            except Exception as e:
                print(f"⚠️ Could not load blob_state color: {e}")

        colors.append(primary_color)

        # --- Step 4: Add secondary emotional tones
        emotion_scores = {k: v for k, v in current.items()
                        if k in self.emotion_colors and v > 0.1}
        sorted_emotions = sorted(emotion_scores.items(),
                                key=lambda x: x[1], reverse=True)[1:4]

        for emotion, score in sorted_emotions:
            color = self.emotion_colors.get(emotion, (128, 128, 128))
            blended = self._blend_colors(primary_color, color, score)
            colors.append(blended)

        # --- Step 5: Fade in emotional memory (last 3)
        if history:
            for entry in history[-3:]:
                hist_emotion = entry.get('primary_emotion', 'neutral')
                hist_color = self.emotion_colors.get(hist_emotion, (128, 128, 128))
                faded = self._fade_color(hist_color, 0.3)
                colors.append(faded)

        # --- Step 6: Safety – ensure variety
        while len(colors) < 3:
            colors.append(primary_color)

        return colors[:5]

    
    def _calculate_blob_parameters(self, current: Dict, history: List[Dict]) -> Dict:
        """
        Calculate blob shape parameters based on emotional state.
        """
        sentiment = current.get('sentiment_polarity', 0.0)
        primary_score = current.get('primary_emotion_score', 0.5)
        
        # Base radius increases with emotional intensity
        base_radius = 200 + int(primary_score * 150)
        
        # Variation based on emotional volatility
        if len(history) > 1:
            # Calculate emotional volatility (how much emotions change)
            volatilities = []
            for i in range(min(5, len(history) - 1)):
                diff = abs(history[-i-1].get('sentiment_polarity', 0) - 
                          history[-i-2].get('sentiment_polarity', 0))
                volatilities.append(diff)
            avg_volatility = sum(volatilities) / len(volatilities) if volatilities else 0.5
            variation = 40 + int(avg_volatility * 80)
        else:
            variation = 60
        
        # Seed for reproducibility with some randomness
        seed = abs(hash(current.get('primary_emotion', 'neutral'))) % 1000
        
        # Complexity based on emotional diversity
        emotion_count = sum(1 for k, v in current.items() 
                           if k in self.emotion_colors and v > 0.15)
        complexity = min(emotion_count + 8, 16)
        
        return {
            'radius': base_radius,
            'variation': variation,
            'seed': seed,
            'complexity': complexity,
            'sentiment': sentiment
        }
    
    def _get_emotion_shape_base(self, emotion: str, center: Tuple[int, int], radius: int, points: int = 360) -> List[Tuple[int, int]]:
        """
        Generate base shape contours before applying organic deformation.
        Each emotion gets a unique geometric feel.
        """
        cx, cy = center
        shape_points = []

        for i in range(points):
            angle = (i / points) * 2 * math.pi

            if emotion == 'joy':
                r = radius  # smooth circle
            elif emotion == 'sadness':
                r = radius * (0.9 + 0.1 * math.sin(angle))  # teardrop feel
                if angle > math.pi:
                    r *= 1.2
            elif emotion == 'anger':
                r = radius * (1 + 0.4 * math.sin(5 * angle))  # sharp spikes
            elif emotion == 'fear':
                r = radius * (1 + 0.25 * math.sin(9 * angle))  # jittery spikes
            elif emotion == 'love':
                # parametric heart formula
                t = angle
                x = 16 * math.sin(t)**3
                y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
                shape_points.append((cx + x * radius * 0.05, cy - y * radius * 0.05))
                continue
            elif emotion == 'anxiety':
                r = radius * (1 - 0.3 * math.sin(6 * angle))  # inward coils
            elif emotion == 'excitement':
                r = radius * (1 + 0.5 * math.sin(8 * angle))  # bursting shape
            elif emotion == 'disgust':
                r = radius * (1 + 0.2 * math.sin(3 * angle + math.sin(angle * 6)))  # irregular
            elif emotion == 'surprise':
                r = radius * (1 + 0.35 * math.sin(4 * angle))  # starburst
            else:  # neutral or undefined
                r = radius

            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            shape_points.append((x, y))

        return shape_points



    def _generate_organic_blob(
            self,
            center: Tuple[int, int],
            base_radius: int,
            variation: int,
            seed: int
        ) -> List[Tuple[int, int]]:
        """
        Generate organic blob shape using perlin-like noise and emotion-based geometry.
        """
        # Use the emotion-aware base shape
        emotion = getattr(self, "current_emotion", "neutral")
        base_points = self._get_emotion_shape_base(
            emotion=emotion,
            center=center,
            radius=base_radius
        )

        np.random.seed(seed)
        points = []

        num_points = len(base_points)
        cx, cy = center

        for i, (bx, by) in enumerate(base_points):
            angle = (i / num_points) * 2 * math.pi

            # Multi-frequency organic distortion
            noise = (
                math.sin(angle * 3 + seed * 0.1) * 0.3
                + math.sin(angle * 5 + seed * 0.2) * 0.2
                + math.sin(angle * 7 + seed * 0.3) * 0.1
                + np.random.uniform(-0.1, 0.1)
            )

            # Distance from center (how far the base point is)
            dx = bx - cx
            dy = by - cy
            dist = math.sqrt(dx * dx + dy * dy)

            # Apply small perturbation based on variation & noise
            factor = 1 + (noise * variation / base_radius)

            x = cx + dx * factor
            y = cy + dy * factor
            points.append((x, y))

        return points

    
    def _draw_layered_blob(self, image: Image, points: List[Tuple[int, int]], 
                           colors: List[Tuple[int, int, int]], 
                           params: Dict):
        """
        Draw multi-layered blob with gradient effects.
        """
        # Create multiple layers for depth
        layers = []
        
        # Background layer (largest, most faded)
        layer1 = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw1 = ImageDraw.Draw(layer1)
        expanded_points = self._expand_points(points, 1.2)
        color1 = colors[0] + (int(255 * 0.2),)  # 20% opacity
        draw1.polygon(expanded_points, fill=color1)
        layer1 = layer1.filter(ImageFilter.GaussianBlur(radius=40))
        layers.append(layer1)
        
        # Middle layer
        layer2 = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw2 = ImageDraw.Draw(layer2)
        color2 = self._blend_colors(colors[0], colors[1] if len(colors) > 1 else colors[0], 0.6)
        color2 = color2 + (int(255 * 0.4),)
        draw2.polygon(points, fill=color2)
        layer2 = layer2.filter(ImageFilter.GaussianBlur(radius=25))
        layers.append(layer2)
        
        # Main layer
        layer3 = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw3 = ImageDraw.Draw(layer3)
        contracted_points = self._expand_points(points, 0.85)
        color3 = colors[0] + (int(255 * 0.7),)
        draw3.polygon(contracted_points, fill=color3)
        layer3 = layer3.filter(ImageFilter.GaussianBlur(radius=15))
        layers.append(layer3)
        
        # Core layer (brightest)
        layer4 = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw4 = ImageDraw.Draw(layer4)
        core_points = self._expand_points(points, 0.6)
        # Brighten core color
        core_color = tuple(min(255, int(c * 1.3)) for c in colors[0])
        core_color = core_color + (int(255 * 0.9),)
        draw4.polygon(core_points, fill=core_color)
        layer4 = layer4.filter(ImageFilter.GaussianBlur(radius=10))
        layers.append(layer4)
        
        # Composite all layers
        result = image.convert('RGBA')
        for layer in layers:
            result = Image.alpha_composite(result, layer)
        
        # Blend gently with previous state for evolution feel
        final = Image.blend(image.convert('RGBA'), result.convert('RGBA'), alpha=0.65)

        # Preserve older colors softly (use additive brightening)
        image.paste(final, (0, 0), final)


    
    def _expand_points(self, points: List[Tuple[int, int]], 
                      factor: float) -> List[Tuple[int, int]]:
        """Expand or contract points from center"""
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)
        
        expanded = []
        for x, y in points:
            dx = x - center_x
            dy = y - center_y
            new_x = center_x + dx * factor
            new_y = center_y + dy * factor
            expanded.append((int(new_x), int(new_y)))
        
        return expanded
    
    def _apply_glow_effect(self, image: Image, color: Tuple[int, int, int]) -> Image:
        """Apply time- and emotion-based outer glow"""
        # Subtle time-based pulsing
        t = time.time() % 4  # 4-second pulse cycle
        pulse = 0.3 + 0.2 * math.sin(t * math.pi / 2)  # oscillate between 0.3 - 0.5

        glow = image.copy()
        glow = glow.filter(ImageFilter.GaussianBlur(radius=60 * pulse))

        blended = Image.blend(image, glow, alpha=pulse)

        # Emotion-based tint overlay
        if getattr(self, "current_emotion", None) in ['anger', 'excitement', 'fear']:
            overlay = Image.new('RGBA', self.size, color + (int(40 + 40 * pulse),))
            blended = Image.alpha_composite(blended, overlay)
        
        return blended

    
    def _apply_smooth_blur(self, image: Image) -> Image:
        """Subtle motion blur effect to simulate organic movement"""
        # Random small drift each frame
        dx = int(np.random.uniform(-1, 1))
        dy = int(np.random.uniform(-1, 1))
        drifted = Image.new('RGBA', self.size, (0, 0, 0, 0))
        drifted.paste(image, (dx, dy))
        
        # Blend with blur
        smooth = drifted.filter(ImageFilter.GaussianBlur(radius=3))
        return Image.blend(image, smooth, alpha=0.6)

    
    def _add_texture(self, image: Image) -> Image:
        """Add subtle noise texture"""
        pixels = np.array(image)
        noise = np.random.randint(-5, 5, pixels.shape, dtype=np.int16)
        pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(pixels)
    
    def _blend_colors(self, color1: Tuple[int, int, int], 
                     color2: Tuple[int, int, int], 
                     ratio: float) -> Tuple[int, int, int]:
        """Blend two colors"""
        return tuple(int(c1 * (1 - ratio) + c2 * ratio) 
                    for c1, c2 in zip(color1, color2))
    
    def _fade_color(self, color: Tuple[int, int, int], 
                   factor: float) -> Tuple[int, int, int]:
        """Fade color towards gray"""
        gray = (128, 128, 128)
        return self._blend_colors(color, gray, 1 - factor)
    
    def generate_static_snapshot(self, emotion_data: Dict) -> BytesIO:
        """
        Generate a single static blob for a specific moment.
        Useful for individual entry visualization.
        """
        return self.generate_evolution_blob([], emotion_data, None)