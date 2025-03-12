import numpy as np
import random

class Individual:
    def __init__(self, chromosome_length):
        self.chromosome_length = chromosome_length
        self.chromosome = self.random_chromosome()
        self.fitness = self.calculate_fitness()

    def random_chromosome(self):
        return np.random.randint(2, size=self.chromosome_length)

    def calculate_fitness(self):
        # Example: Maximize the sum of the bits in the chromosome
        return sum(self.chromosome)

    def mutate(self, mutation_rate):
        for index in range(self.chromosome_length):
            if random.random() < mutation_rate:
                self.chromosome[index] = 1 - self.chromosome[index]  # Flip the bit

class GeneticAlgorithm:
    def __init__(self, population_size, chromosome_length, mutation_rate, generations):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.population = self.create_initial_population()

    def create_initial_population(self):
        return [Individual(self.chromosome_length) for _ in range(self.population_size)]

    def select_parents(self):
        # Simple tournament selection
        tournament_size = 3
        parent1 = self.tournament_selection(tournament_size)
        parent2 = self.tournament_selection(tournament_size)
        return parent1, parent2

    def tournament_selection(self, tournament_size):
        selection_indices = random.sample(range(self.population_size), tournament_size)
        selected = [self.population[i] for i in selection_indices]
        return max(selected, key=lambda ind: ind.fitness)

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, self.chromosome_length - 1)
        child1_chromosome = np.concatenate((parent1.chromosome[:crossover_point], parent2.chromosome[crossover_point:]))
        child2_chromosome = np.concatenate((parent2.chromosome[:crossover_point], parent1.chromosome[crossover_point:]))
        return Individual(self.chromosome_length), Individual(self.chromosome_length)

    def evolve(self):
        for generation in range(self.generations):
            new_population = []
            while len(new_population) < self.population_size:
                parent1, parent2 = self.select_parents()
                child1, child2 = self.crossover(parent1, parent2)
                child1.mutate(self.mutation_rate)
                child2.mutate(self.mutation_rate)
                new_population.append(child1)
                new_population.append(child2)
            self.population = new_population[:self.population_size]
            self.evaluate_population()
            best_individual = max(self.population, key=lambda ind: ind.fitness)
            print(f"Generation {generation}: Best Fitness = {best_individual.fitness}")

    def evaluate_population(self):
        for individual in self.population:
            individual.fitness = individual.calculate_fitness()

if __name__ == "__main__":
    population_size = 100
    chromosome_length = 20
    mutation_rate = 0.01
    generations = 50

    ga = GeneticAlgorithm(population_size, chromosome_length, mutation_rate, generations)
    ga.evolve()

    best_individual = max(ga.population, key=lambda ind: ind.fitness)
    print(f"Best Individual: {best_individual.chromosome} with Fitness = {best_individual.fitness}")