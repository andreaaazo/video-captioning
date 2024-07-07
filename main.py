from src.captioning_pipeline import CaptioningPipeline


def main():
    pipeline = CaptioningPipeline(
        "data/example.mp4", "data/font.ttf", 100, word_count=2
    )
    pipeline.run()


if __name__ == "__main__":
    main()
