from captioning_pipeline import CaptioningPipeline


def main():
    pipeline = CaptioningPipeline("example.mp4", "font.ttf", 100)
    pipeline.run()


if __name__ == "__main__":
    main()
