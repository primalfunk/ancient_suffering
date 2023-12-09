import logging_config
import logging
import random
from enemy import Enemy
from room import Room

class CombatSimulation:
    def __init__(self, num_simulations=1000):
        logging_config.setup_logging()
        self.battle_room = Room(1, 1, 1)
        self.num_simulations = num_simulations
        self.sim_logger = logging.getLogger('sim')
        
    def simulate_fight(self, c1, c2):
        rounds, hits, criticals = 0, 0, 0
        while c1.hp > 0 and c2.hp > 0:
            rounds += 1
            # c1's turn
            damage, critical_hit = self.simulated_attack(c1, c2)
            if damage > 0:
                hits += 1
            if critical_hit:
                criticals += 1
            if c2.hp <= 0:
                break
            # c2's turn
            self.simulated_attack(c2, c1)  # c2's attack on c1, no need to track hits/criticals for c2
        winner = c1 if c1.hp > 0 else c2
        return rounds, winner, hits, criticals
    
    def simulated_attack(self, attacker, defender):
        dodge_chance = 10  # 10% chance to dodge
        if random.randint(0, 100) < dodge_chance:
            return 0, False  # No damage, no critical hit
        if random.random() < 0.1:  # 10% chance of a luck boost
            luck_boost = 1.3  # 30% increase in stats
            attacker.atk *= luck_boost
            attacker.defn *= luck_boost
            attacker.eva *= luck_boost
        critical_hit = False
        hit_chance = max(0, min(100, 50 + (attacker.int - defender.eva) / 4))
        hit = random.randint(0, 100) < hit_chance
        damage = 0
        if hit:
            attack_variance = random.uniform(0.6, 2)
            defense_variance = random.uniform(0.6, 2) 
            damage = max(2, (attacker.atk * attack_variance) - (defender.defn * defense_variance))
            # Enhanced critical hit mechanics
            base_critical_chance = 33  # Increased base critical chance
            critical_hit_chance = base_critical_chance + (attacker.wis - defender.wis) / 4
            critical_hit = random.randint(0, 100) < critical_hit_chance
            if critical_hit:
                damage *= 3
            defender.hp -= damage
        return damage, critical_hit

    def run_sweep_simulation(self, l1, level_range, scaling_attr, scaling_factor, sweep_range, step_count):
        initial_value = getattr(Enemy(self.battle_room, l1, scaling_attr, scaling_factor), scaling_attr)
        start_value = initial_value - sweep_range
        end_value = initial_value + sweep_range
        step_size = (end_value - start_value) / step_count
        simulation_results = {}

        for i in range(step_count + 1):
            current_value = start_value + i * step_size
            results_lower, results_higher = self.run_single_sweep(l1, level_range, current_value, scaling_attr, scaling_factor)
            win_rate_c1_lower = results_lower[1]  # Win rate for c1 in the lower-level matchup
            win_rate_c1_higher = results_higher[1]  # Win rate for c1 in the higher-level matchup
            simulation_results[current_value] = (win_rate_c1_lower, win_rate_c1_higher)

        return simulation_results

    def run_single_sweep(self, l1, level_range, current_value, scaling_attr, scaling_factor):
        results_lower = self.run_simulation(l1, l1 - level_range, scaling_attr, scaling_factor)
        results_higher = self.run_simulation(l1, l1 + level_range, scaling_attr, scaling_factor)
        return results_lower, results_higher

    def run_simulation(self, l1, l2):
        level1, level2 = l1, l2
        c1_wins, c2_wins, total_rounds = 0, 0, 0
        total_hits, total_criticals = 0, 0
        total_stats_c1 = {'atk': 0, 'defn': 0, 'int': 0, 'wis': 0, 'con': 0, 'eva': 0, 'max_hp': 0}
        total_stats_c2 = {'atk': 0, 'defn': 0, 'int': 0, 'wis': 0, 'con': 0, 'eva': 0, 'max_hp': 0}
        for _ in range(self.num_simulations):
            c1, c2 = self.prepare_combatants(level1, level2)
            rounds, winner, hits, criticals = self.simulate_fight(c1, c2)
            total_rounds += rounds
            total_hits += hits
            total_criticals += criticals
            if winner == c1:
                c1_wins += 1
            else:
                c2_wins += 1
            for stat in total_stats_c1:
                total_stats_c1[stat] += getattr(c1, stat)
                total_stats_c2[stat] += getattr(c2, stat)
        avg_rounds = total_rounds / self.num_simulations
        win_rate = c1_wins / self.num_simulations
        hit_rate = total_hits / self.num_simulations
        crit_rate = total_criticals / self.num_simulations
        avg_stats_c1 = {stat: round(total_stats_c1[stat] / self.num_simulations, 1) for stat in total_stats_c1}
        avg_stats_c2 = {stat: round(total_stats_c2[stat] / self.num_simulations, 1) for stat in total_stats_c2}
        stat_diffs = {stat: round(avg_stats_c1[stat] - avg_stats_c2[stat], 1) for stat in avg_stats_c1}

        print(f"Rounds: {avg_rounds:.1f}, Win Rate: {win_rate:.2f}, Hit Rate: {hit_rate:.1f}, Crit Rate: {crit_rate:.1f}, Stat Differences: {stat_diffs}")
        return avg_rounds, win_rate, hit_rate, crit_rate, stat_diffs
    
    def prepare_combatants(self, level1, level2):
            c1 = Enemy(self.battle_room, level1)
            c2 = Enemy(self.battle_room, level2)
            return c1, c2

    # def find_optimal_scaling(self, l1, level_range, sweep_range, step_count):
    #     print("Starting find_optimal_scaling operation")
    #     optimal_combinations = []

    #     for attr in attributes_to_test:
    #         for factor in scaling_factors:
    #             print(f"Testing attribute: {attr}, Scaling Factor: {factor}")
    #             simulation_results = self.run_sweep_simulation(l1, level_range, attr, factor, sweep_range, step_count)

    #             for current_value, (win_rate_c1_lower, win_rate_c1_higher) in simulation_results.items():
    #                 print(f"Attr: {attr}, Factor: {factor}, Value: {current_value}, Win Rates: {win_rate_c1_lower}, {win_rate_c1_higher}")
    #                 if self.meets_criteria(win_rate_c1_lower, win_rate_c1_higher):
    #                     print(f"Optimal combination found: Attribute: {attr}, Scaling Factor: {factor}, Value: {current_value}")
    #                     optimal_combinations.append((attr, factor, current_value))

    #     print("find_optimal_scaling operation completed")
    #     return optimal_combinations

    def meets_criteria(self, win_rate_c1, win_rate_c2):
        # Define thresholds for the win rates
        threshold_c1 = 0.90  # 90% win rate for c1
        threshold_c2 = 0.10  # 10% win rate for c2

        # Check if the win rates are within the desired range
        return win_rate_c1 >= threshold_c1 and win_rate_c2 >= threshold_c2


c = CombatSimulation()
# attributes_to_test = ['atk', 'defn', 'int', 'wis', 'con', 'eva']
# scaling_factors = [0.2, 0.25, 0.3, 0.35]  # Adjust this range as needed
# optimal_combinations = c.find_optimal_scaling(l1=10, level_range=2, sweep_range=20, step_count=20)
# print(f"Finished. Successful combos listed now:")
# for combo in optimal_combinations:
#     print(f"Attribute: {combo[0]}, Scaling Factor: {combo[1]}, Value: {combo[2]}")
c.run_simulation(10, 14)
c.run_simulation(10, 6)