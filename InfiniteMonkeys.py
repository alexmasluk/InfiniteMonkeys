from lcs import LCS
from tkinter import *
import random
import operator
import statistics
import time

class InfiniteMonkeys():
    def __init__(self, master):
        self.target = ''
        self.genetic_material = ''
        self.low_chance = 0.1
        self.med_chance = 0.5
        self.high_chance = 0.9
        self.pop_size = 350
        self.radiation_level = 0.2    #controls mutation chance
        self.disaster_threshold = 0.15 #controls deadliness of disasters
        self.disaster_period = 50   #num generations before disaster
        self.output_var = StringVar()
        self.master = master
        self.button = Button(
                self.master, text="GO", fg="red", command=self.do_genetics
                )
        self.button.pack(side=LEFT)
        self.label = Text(
                self.master, textvariable = self.output_var
                )
        self.label.pack(side=RIGHT)
    

    def strcmp(self,a,b):
        score = []
        for x in range(len(a)):
            if a[x] == b[x]:
                score.append(1)
            else:
                score.append(0)
        return statistics.mean(score)

    def fitness_func(self,a):
        if len(a) == len(self.target):
            fit = self.strcmp(a,self.target)
        else:
            fit = LCS(a,self.target)

        return fit

    def gen(self, size, rand_length=False):
        if rand_length:
            size = random.randint(2, len(self.target) * 2)

        dna = ''.join(random.choice(self.genetic_material) for _ in range(size))
        return dna

    def evaluate(self, pop):
        new_pop = [] 
        pop_fitness = []
        for ind in pop:
            fitness = self.fitness_func(ind)
            pop_fitness.append(fitness)
            new_pop.append( (ind,fitness) )
    
        high_med = statistics.median_high(pop_fitness)
        low_med = statistics.median_low(pop_fitness)

        #individuals with high fitness have better chance to reproduce
        selected_pop = []    
        for ind in new_pop:
            chance_selected = ind[1]
            if ind[1] < low_med:
                chance_selected = self.low_chance
            if ind[1] > high_med:
                chance_selected = self.high_chance 
            selected_pop.append( (ind[0], chance_selected) )
        return selected_pop

    def find_parent(self, pop, index):
        while True:
            if index >= self.pop_size:
                index = 0
            candidate = pop[index]
            chance = candidate[1]
            reproduce = random.randint(0,1000) < 1000 * chance
            index += 1
            if reproduce == True:
                return candidate[0], index

    def reproduce(self, pop):
        new_pop = []
        loop_index = random.randint(0,self.pop_size) 
        while len(new_pop) < self.pop_size:
            mom, loop_index = self.find_parent(pop, loop_index)
            dad, loop_index = self.find_parent(pop, loop_index)

            x_pt = random.randint(0, len(self.target)-1)
            child = mom[:x_pt] + dad[x_pt:]
            new_child = ''
            mutate = random.randint(0,1000) < 1000 * self.radiation_level
            if mutate:
                gene = random.randint(0,len(self.target)-1)
            for x, letter in enumerate(child):
                if mutate and x == gene:
                    new_child +=random.choice(self.genetic_material)
                else:
                    new_child += child[x]
            new_pop.append(new_child)
            #print("M:{} D:{} C:{}".format(mom, dad, child))

        return new_pop
    
    def natural_disaster(self, pop):
        print(random.choice(["flood!", "plague!", "fire!", "holocaust!", "meteor strike!", "global warming!", "nuclear fallout!", "rogue AI!"]))
        cutoff = int(self.pop_size * self.disaster_threshold) 
        pop = pop[cutoff:]
        while len(pop) < self.pop_size:
            pop.append(self.gen(len(self.target)))
        return pop

    def init_population(self):
        with open("target_text.txt", encoding='utf8') as f:
            self.target = f.read()
        self.genetic_material = ''
        for letter in self.target:
            if letter not in self.genetic_material:
                self.genetic_material += letter

        population = []
        for x in range(self.pop_size):
            newborn = self.gen(len(self.target))
            population.append(newborn)

        return population
            
    def do_genetics(self):
        try:

            start = time.time()
            population = self.init_population()
            count = 1
            fitness_history = 0 
            improvement_history = 0
            last_avg_fitness = 0
            
            while True:
                #assign reproductive probability to each 7individual
                population = self.evaluate(population)
                #generate new members
                population = self.reproduce(population)

                #display/update population summary data for this generation
                best_individual = population[0]
                max_fitness = self.fitness_func(best_individual)
                total_local_fitness = 0
                for individual in population:
                    fitness = self.fitness_func(individual)
                    total_local_fitness += fitness
                    if fitness > max_fitness:
                        max_fitness = fitness
                        best_individual = individual
                fitness_history += max_fitness
                avg_fitness = total_local_fitness / self.pop_size
                if avg_fitness > last_avg_fitness:
                    improvement_history += 1
                last_avg_fitness = avg_fitness

                output = "gen:{:06d}\n{}\nfitness:{:0.3f} | running_fit_avg:{:0.3f} | improvement_average:{:0.3f}\n".format(count, best_individual, max_fitness, avg_fitness, improvement_history / count)
                self.output_var.set(output)
                self.master.update_idletasks() 
                count += 1

                #if solution was found exit
                if best_individual == self.target:
                    seconds = time.time() - start
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    print("Singularity achieved in {:03d}:{:02d}:{:02d}".format(int(h), int(m), int(s)))
                    return

                #every N generations we need fresh genes
                if count != 0 and count % self.disaster_period == 0:
                    population = self.natural_disaster(population)

        except KeyboardInterrupt:
            for ind in population:
                print(self.fitness_func(ind))
            return

def main():
    root = Tk()
    infinte_monkeys = InfiniteMonkeys(root)
    root.mainloop()
    root.destroy()
        

if __name__ == "__main__":
    main()
