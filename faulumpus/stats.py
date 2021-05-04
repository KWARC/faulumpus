from generate import WorldGenerator


generator = WorldGenerator()
pits = []

for i in range(10000):
    print(f'{generator.stats_created:6}/{generator.stats_attempted:6}')
    w = generator.makeWorld()
    pits.append(sum(s.pit for s in w.squares()))

print(sum(pits)/len(pits))  # 13.2243
